from django.utils import timezone
from celery import shared_task
from utils.logging_utils import get_logger
import time
from django.utils import timezone

# assistants/tasks.py
from mcp_core.models import Tag
from django.utils.text import slugify
from openai import OpenAI
from assistants.helpers.memory_utils import tag_text

from prompts.utils.token_helpers import EMBEDDING_MODEL
from assistants.utils.session_utils import load_session_messages, flush_chat_session

from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from embeddings.helpers.helpers_io import save_embedding
from memory.models import MemoryEntry, GlossaryRetryLog
from mcp_core.models import MemoryContext, NarrativeThread
from assistants.models.assistant import (
    Assistant,
    DelegationEvent,
)
from assistants.models.project import AssistantProject
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.reflection import (
    AssistantReflectionInsight,
    AssistantReflectionLog,
)

client = OpenAI()

logger = get_logger("assistants")


@shared_task
def archive_expired_assistant_sessions():
    """
    Scan Redis for expired assistant chat sessions and archive them into MemoryContext.
    """
    from redis import Redis
    import os

    r = Redis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"))

    keys = r.keys("chat:*:meta")
    logger.info(f"🔍 Checking {len(keys)} session meta keys...")

    for meta_key in keys:
        try:
            session_id = meta_key.decode().split(":")[1]
            meta = r.hgetall(meta_key)
            expires_at = float(meta.get(b"expires_at", 0))

            if timezone.now().timestamp() < expires_at:
                continue  # still active

            # Load chat messages
            messages = load_session_messages(session_id)
            if not messages:
                continue

            # Construct archive
            archive_text = "\n".join(
                [f"{m['role'].capitalize()}: {m['content']}" for m in messages]
            )

            assistant_id = meta.get(b"assistant_id", b"").decode()
            from utils.resolvers import resolve_or_error
            from django.core.exceptions import ObjectDoesNotExist

            try:
                assistant = resolve_or_error(assistant_id, Assistant)
            except ObjectDoesNotExist:
                assistant = None

            # Save to DB memory
            memory = MemoryContext.objects.create(
                target_type="assistant_chat",
                target_id=session_id,
                content=archive_text,
                category="chat_archive",
                tags=["assistant", assistant.slug if assistant else "unknown"],
                important=True,
            )
            save_embedding(memory, embedding=[])

            # Cleanup
            flush_chat_session(session_id)
            logger.info(
                f"✅ Archived session {session_id} with {len(messages)} messages."
            )

        except Exception as e:
            logger.error(f"❌ Error archiving session {meta_key}: {e}", exc_info=True)


@shared_task(bind=True, max_retries=3, default_retry_delay=15)
def embed_and_tag_memory(self, memory_id: int):
    try:
        memory = MemoryEntry.objects.get(id=memory_id)
        transcript = memory.full_transcript.strip()

        if not transcript:
            logger.warning(f"⚠️ Memory {memory_id} has empty transcript. Skipping.")
            return

        # Embedding
        start = time.time()
        embedding_response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=transcript,
        )

        if not embedding_response.data:
            logger.warning(f"⚠️ No embedding returned for memory {memory.id}. Skipping.")
            return

        vector = embedding_response.data[0].embedding
        if (
            vector is None
            or (hasattr(vector, "__len__") and len(vector) == 0)
            or not any(vector)
        ):
            logger.warning(f"❌ Skipping memory {memory.id} — empty or invalid vector")
            return

        save_embedding(memory, vector)
        logger.info(
            f"⏱ Embedding complete for Memory {memory.id} in {time.time() - start:.2f}s"
        )

        # Step 2: Link memory to assistant (via related project, if available)
        if memory.related_project and memory.related_project.assistant:
            memory.assistant = memory.related_project.assistant

        # Step 3: Tag the memory (create tags if needed)
        tag_objs = tag_text(transcript)
        memory.tags.set(tag_objs)
        tag_names = [tag.name for tag in tag_objs]
        logger.info(f"🏷 Memory {memory.id} tagged with: {', '.join(tag_names)}")

        # Step 4: Optionally link to the most recent thought from that assistant
        if memory.assistant:
            latest_thought = (
                AssistantThoughtLog.objects.filter(assistant=memory.assistant)
                .order_by("-created_at")
                .first()
            )
            if latest_thought:
                memory.linked_thought = latest_thought

        # Step 5: Save everything and update freshness
        memory.vector_updated_at = timezone.now()
        memory.save()

        logger.info(
            f"[🧠] Memory {memory.id} embedded, tagged, and saved with {len(tag_objs)} tags."
        )

    except Exception as e:
        logger.error(f"❌ Failed to embed/tag memory {memory_id}: {e}", exc_info=True)
        self.retry(exc=e)


@shared_task(bind=True)
def run_assistant_reflection(self, memory_id: int):
    try:
        memory = MemoryEntry.objects.select_related("assistant").get(id=memory_id)

        if not memory.assistant:
            return (
                f"❌ No assistant attached to memory {memory_id}. Skipping reflection."
            )

        engine = AssistantReflectionEngine(memory.assistant)
        if not memory.context:
            memory.context = memory.assistant.memory_context
            memory.save(update_fields=["context"])
        ref_log = engine.reflect_now()
        if not ref_log:
            return "🧠 No relevant entries to reflect on."

        if memory.anchor:
            try:
                log = (
                    GlossaryRetryLog.objects.filter(anchor=memory.anchor)
                    .order_by("-created_at")
                    .first()
                )
                if log and log.retried:
                    outcome = "succeeded" if log.score_diff > 0 else "failed"
                    line = f"User asked about {memory.anchor.label}; glossary was injected, but initial answer ignored context. Retry {outcome}."
                else:
                    line = f"User asked about {memory.anchor.label}; glossary definition used and reflected in answer."
                memory.summary = (
                    memory.summary + "\n" if memory.summary else ""
                ) + line
                memory.save(update_fields=["summary"])
            except Exception:
                logger.exception("Failed to update memory summary")

        return f"🧠 Reflection complete: {ref_log.summary[:80]}..."

    except Exception as e:
        self.retry(exc=e, countdown=10, max_retries=3)


@shared_task(bind=True)
def reflect_on_spawned_assistant(
    self,
    parent_id: str,
    assistant_id: str,
    project_id: str,
    thread_id: str | None = None,
):
    """Run reflection on a newly spawned assistant and log under the parent."""
    from utils.resolvers import resolve_or_error
    from django.core.exceptions import ObjectDoesNotExist

    try:
        parent = resolve_or_error(parent_id, Assistant)
        new_assistant = resolve_or_error(assistant_id, Assistant)
        project = AssistantProject.objects.get(id=project_id)
        thread = None
        if thread_id:
            thread = NarrativeThread.objects.filter(id=thread_id).first()

        engine = AssistantReflectionEngine(parent)
        ref_log = engine.reflect_on_assistant(new_assistant, project)

        AssistantThoughtLog.objects.create(
            assistant=parent,
            project=project,
            thought=ref_log.summary,
            thought_type="reflection",
            linked_reflection=ref_log,
            narrative_thread=thread,
        )

        return ref_log.summary
    except Exception as e:
        logger.error("Failed to reflect on spawned assistant: %s", e, exc_info=True)
        self.retry(exc=e, countdown=10, max_retries=3)


@shared_task(bind=True)
def reflect_on_delegation(self, event_id: str):
    """Generate a reflection about a ``DelegationEvent``."""
    try:
        event = DelegationEvent.objects.select_related(
            "parent_assistant",
            "child_assistant",
            "triggering_session",
            "triggering_memory",
        ).get(id=event_id)

        parent = event.parent_assistant
        child = event.child_assistant

        prompt = (
            f"You are {parent.name} reflecting on delegating work to {child.name}.\n"
            f"Reason for delegation: {event.reason}\n\n"
            "Provide a brief reflection on this decision and any next steps."
        )

        engine = AssistantReflectionEngine(parent)
        ref_log = engine.generate_reflection(prompt)
        # engine.generate_reflection returns str; create log
        reflection_log = AssistantReflectionLog.objects.create(
            assistant=parent,
            project=project,
            summary=ref_log,
            raw_prompt=prompt,
            title="Delegation Reflection",
        )

        project = None
        thread = None
        if event.triggering_session:
            project = event.triggering_session.project
            thread = event.triggering_session.narrative_thread
        if not thread and event.triggering_memory:
            thread = (
                event.triggering_memory.thread
                or event.triggering_memory.narrative_thread
            )

        AssistantThoughtLog.objects.create(
            assistant=parent,
            project=project,
            thought=ref_log,
            thought_type="reflection",
            category="reflection",
            narrative_thread=thread,
            thought_trace=f"child_assistant:{child.id}",
            linked_reflection=reflection_log,
        )

        return ref_log
    except Exception as e:
        logger.error(
            "Failed to reflect on delegation %s: %s", event_id, e, exc_info=True
        )
        self.retry(exc=e, countdown=10, max_retries=3)


@shared_task
def delegation_health_check():
    """Analyze recent delegation events and log warnings for failing agents."""
    from django.db.models import Avg

    week_ago = timezone.now() - timezone.timedelta(days=7)
    for assistant in Assistant.objects.filter(is_active=True):
        recent = DelegationEvent.objects.filter(
            child_assistant=assistant, created_at__gte=week_ago
        )
        failures = recent.filter(score__lte=2).count()
        if failures >= 3:
            avg = recent.aggregate(avg=Avg("score"))["avg"] or 0
            AssistantThoughtLog.objects.create(
                assistant=assistant,
                thought_type="reflection",
                category="warning",
                thought=f"Agent had {failures} failures in last week. Avg score {avg:.2f}",
            )


from assistants.utils.drift_detection import (
    analyze_drift_for_assistant,
    analyze_specialization_drift,
)
from assistants.models.assistant import SpecializationDriftLog


def run_specialization_drift_checks():
    """Run drift analysis using both lightweight and logged methods."""
    for assistant in Assistant.objects.filter(is_active=True):
        analyze_drift_for_assistant(assistant)
        result = analyze_specialization_drift(assistant)
        if result.get("flagged"):
            SpecializationDriftLog.objects.create(
                assistant=assistant,
                drift_score=result["drift_score"],
                summary=result["summary"],
                trigger_type="auto",
                auto_flagged=True,
                requires_retraining=result.get("requires_retraining", False),
            )


@shared_task
def run_drift_check_for_assistant(assistant_id: str):
    """Run drift check for a single assistant."""
    from utils.resolvers import resolve_or_error
    from django.core.exceptions import ObjectDoesNotExist

    try:
        assistant = resolve_or_error(assistant_id, Assistant)
    except ObjectDoesNotExist:
        assistant = None

    if assistant:
        log = analyze_drift_for_assistant(assistant)
        return str(log.id) if log else None


def _simple_emotion_detect(text: str):
    """Very basic keyword-based emotion detection."""
    lowered = text.lower()
    if any(w in lowered for w in ["happy", "glad", "joy"]):
        return "joy", 0.8
    if any(w in lowered for w in ["sad", "unhappy", "depress"]):
        return "sadness", 0.8
    if any(w in lowered for w in ["angry", "frustrated", "mad"]):
        return "frustration", 0.7
    if any(w in lowered for w in ["curious", "interesting", "wonder"]):
        return "curiosity", 0.6
    return "neutral", 0.0


@shared_task
def detect_emotional_resonance(memory_id: str):
    from memory.models import MemoryEntry
    from assistants.models import EmotionalResonanceLog

    memory = MemoryEntry.objects.filter(id=memory_id).first()
    if not memory or not memory.assistant:
        return None

    text = memory.full_transcript or memory.event
    emotion, intensity = _simple_emotion_detect(text)

    log = EmotionalResonanceLog.objects.create(
        assistant=memory.assistant,
        source_memory=memory,
        detected_emotion=emotion,
        intensity=float(intensity),
        context_tags=memory.context_tags[:5] if memory.context_tags else [],
    )
    return str(log.id)


@shared_task
def reflect_on_emotional_resonance(assistant_id: str):
    from assistants.models import EmotionalResonanceLog, AssistantThoughtLog, Assistant

    from utils.resolvers import resolve_or_error
    from django.core.exceptions import ObjectDoesNotExist

    try:
        assistant = resolve_or_error(assistant_id, Assistant)
    except ObjectDoesNotExist:
        return "assistant not found"

    logs = EmotionalResonanceLog.objects.filter(assistant=assistant).order_by(
        "-created_at"
    )[:20]
    if not logs:
        return "no resonance"

    avg = sum(l.intensity for l in logs) / len(logs)
    assistant.avg_empathy_score = round(avg, 2)
    assistant.save(update_fields=["avg_empathy_score"])

    summary = f"Avg intensity {avg:.2f} based on {len(logs)} memories"
    AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=summary,
        thought_type="reflection",
        category="insight",
    )
    return summary


@shared_task
def run_council_deliberation(session_id: str):
    """Sequentially log council member thoughts for one round."""
    from django.db.models import Max
    from assistants.models import CouncilSession, CouncilThought

    session = CouncilSession.objects.filter(id=session_id).first()
    if not session:
        return "session not found"

    max_round = session.thoughts.aggregate(max=Max("round"))["max"] or 0
    next_round = max_round + 1

    for member in session.members.all():
        CouncilThought.objects.create(
            assistant=member,
            council_session=session,
            content=f"[{next_round}] {member.name} shares thoughts on {session.topic}.",
            round=next_round,
        )

    return f"round {next_round} completed"


@shared_task
def reflect_on_council(session_id: str):
    """Summarize all thoughts and finalize the session."""
    from assistants.models import CouncilSession, CouncilOutcome

    session = CouncilSession.objects.filter(id=session_id).first()
    if not session:
        return "session not found"

    summary = "\n".join(t.content for t in session.thoughts.order_by("created_at"))
    CouncilOutcome.objects.create(council_session=session, summary=summary)
    session.status = "finished"
    session.save(update_fields=["status"])
    return "ok"


@shared_task
def evaluate_team_alignment_task(project_id: str):
    from assistants.helpers.collaboration import evaluate_team_alignment

    log = evaluate_team_alignment(project_id)
    return str(log.id) if log else None


@shared_task
def log_demo_reflection_task(assistant_id: str, session_id: str):
    from assistants.models import Assistant
    from assistants.helpers.demo_utils import log_demo_reflection

    assistant = Assistant.objects.filter(id=assistant_id, is_demo=True).first()
    if assistant:
        log_demo_reflection(assistant, session_id)


@shared_task
def run_rag_ci_checks(slug: str) -> str:
    """Run RAG validation commands for the given assistant."""
    from django.core.management import call_command
    from assistants.models import Assistant, AssistantDevLog

    assistant = Assistant.objects.filter(slug=slug).first()
    if not assistant:
        return "missing"
    try:
        call_command("repair_all_embeddings")
        call_command("run_rag_tests", "--assistant", slug)
        call_command("log_embedding_drift", "--assistant", slug)
    except Exception as exc:  # pragma: no cover - best effort
        AssistantDevLog.objects.create(
            assistant=assistant, issue_type="cert_failure", details=str(exc)
        )
        return "error"
    return "ok"


@shared_task(rate_limit="4/m")
def reflect_on_document_task(doc_id, assistant_slug=None):
    from django.core.management import call_command

    args = ["--doc", str(doc_id)]
    if assistant_slug:
        args += ["--assistant", assistant_slug]
    call_command("reflect_on_document", *args)


@shared_task(rate_limit="2/m")
def generate_diagnostic_report_task(markdown_only=False):
    from django.core.management import call_command

    if markdown_only:
        call_command("generate_diagnostic_reports", "--markdown-only")
    else:
        call_command("generate_diagnostic_reports")


@shared_task(rate_limit="1/h")
def bootstrap_evo_assistants_task():
    from django.core.management import call_command

    call_command("bootstrap_evo_assistants")
