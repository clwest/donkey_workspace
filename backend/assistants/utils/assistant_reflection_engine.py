import logging
from assistants.models.assistant import Assistant
from assistants.models.project import AssistantProject
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.reflection import (
    AssistantReflectionLog,
    AssistantReflectionInsight,
)
from intel_core.models import DocumentChunk
from mcp_core.models import MemoryContext, DevDoc, NarrativeThread
from intel_core.models import Document
from prompts.models import Prompt
from prompts.utils.token_helpers import count_tokens
from prompts.utils.openai_utils import generate_prompt_from_summary
from mcp_core.utils.log_prompt import log_prompt_usage
from mcp_core.models import Tag
from assistants.models.project import AssistantPromptLink
from memory.models import MemoryEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils import timezone

from agents.models.core import (
    Agent,
    AgentTrainingAssignment,
    AgentFeedbackLog,
    AgentSkill,
    AgentSkillLink,
    AgentCluster,
)

from agents.models.lore import SwarmMemoryEntry
from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.helpers.helpers_io import save_embedding
from agents.utils.swarm_analytics import generate_temporal_swarm_report
import json
from typing import Optional, List
from intel_core.utils.glossary_tagging import _match_anchor
from memory.models import SymbolicMemoryAnchor

logger = logging.getLogger(__name__)


def _skill_names(skills: list) -> list[str]:
    names = []
    for s in skills or []:
        if isinstance(s, dict) and s.get("skill"):
            names.append(s["skill"])
        elif isinstance(s, str):
            names.append(s)
    return names


def generate_first_reflection(assistant: Assistant) -> tuple[str, list[str]]:
    """Generate a short reflection on the assistant's earliest memories."""
    entries = list(
        MemoryEntry.objects.filter(assistant=assistant).order_by("created_at")[:10]
    )
    if not entries:
        return "", []

    anchors = SymbolicMemoryAnchor.objects.all()
    matched = set()
    drift = 0
    user_msgs = 0

    for mem in entries:
        text = mem.summary or mem.event or ""
        if mem.source_role == "user":
            user_msgs += 1
        for anc in anchors:
            found, _ = _match_anchor(anc, text)
            if found:
                matched.add(anc.slug)
                if mem.anchor_id and str(mem.anchor_id) != str(anc.id):
                    drift += 1

    parts = []
    if user_msgs:
        parts.append(f"Exchanged {user_msgs} early user messages.")
    if matched:
        parts.append("Recognized anchors: " + ", ".join(sorted(matched)) + ".")
    if drift:
        parts.append(f"Detected {drift} potential glossary mismatches.")
    if not parts:
        parts.append("No notable glossary activity yet.")

    summary = " ".join(parts)
    ids = [str(m.id) for m in entries]
    return summary, ids


def reflect_on_agent_training(assistant: Assistant, agent: Agent) -> str:
    """
    Generates a reflection summary for an agent's recent training progress.
    Returns a markdown string with bullet points.
    """

    assignments = AgentTrainingAssignment.objects.filter(agent=agent)
    total = assignments.count()
    completed = assignments.filter(completed=True).count()
    completion_rate = completed / total if total else 0.0

    skill_tags = set()
    for a in assignments:
        skill_tags.update(a.document.tags.values_list("name", flat=True))

    feedback_logs = list(
        AgentFeedbackLog.objects.filter(agent=agent, score__isnull=False).order_by(
            "-created_at"
        )[:6]
    )
    recent_scores = [f.score for f in feedback_logs[:3]]
    past_scores = [f.score for f in feedback_logs[3:]]
    recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0.0
    past_avg = sum(past_scores) / len(past_scores) if past_scores else 0.0
    if recent_avg > past_avg + 0.05:
        trajectory = "improving"
    elif recent_avg + 0.05 < past_avg:
        trajectory = "declining"
    else:
        trajectory = "stable"

    readiness = max(agent.readiness_score, completion_rate)

    lines = [
        f"- Training completion rate: {completion_rate:.0%} ({completed}/{total})",
    ]
    if skill_tags:
        lines.append("- Acquired skills: " + ", ".join(sorted(skill_tags)))
    if agent.verified_skills:
        lines.append(
            "- Verified skills: " + ", ".join(_skill_names(agent.verified_skills))
        )
    lines.append(f"- Task performance trajectory appears **{trajectory}**")
    lines.append(f"- Suggested readiness score: {readiness:.2f}")
    lines.append("- Next steps: continue practicing and gather more feedback")

    return "\n".join(lines)


class AssistantReflectionEngine:

    def __init__(self, assistant):
        self.assistant = assistant
        self.context = assistant.memory_context
        self.project = self.get_or_create_project(assistant)
        logger.info(
            f"[ReflectionEngine] Assistant: {assistant.slug}, Context ID: {getattr(self.context, 'id', 'none')}"
        )
        if self.context:
            orphaned = MemoryEntry.objects.filter(
                assistant=self.assistant, context__isnull=True
            ).count()
            if orphaned > 0 and not (
                self.assistant.is_demo
                and (
                    self.assistant.memory_context is None
                    or not self.assistant.assistant_reflections.exists()
                )
            ):
                logger.warning(
                    f"[ReflectionEngine] \u26a0\ufe0f Found {orphaned} orphaned memory entries for {self.assistant.slug}"
                )

    def get_memory_entries(self, limit: int = 30, *, verbose: bool = False):
        """Return prioritized memories eligible for reflection."""
        from django.db.models import Q

        qs = MemoryEntry.objects.filter(assistant=self.assistant)
        total = qs.count()

        skipped_context = 0
        if self.context:
            skipped_context = qs.exclude(context=self.context).count()
            qs = qs.filter(context=self.context)

        skipped_low = qs.filter(importance__lt=1).count()
        qs = qs.filter(importance__gte=1)

        skipped_missing = qs.filter(
            full_transcript__isnull=True, summary__isnull=True
        ).count()
        qs = qs.filter(Q(full_transcript__isnull=False) | Q(summary__isnull=False))

        junk_phrase = "couldn’t find that information"
        skipped_junk = qs.filter(event__icontains=junk_phrase).count()
        qs = qs.exclude(event__icontains=junk_phrase)

        entries = list(qs.order_by("-created_at")[:limit])

        if verbose:
            print(
                f"\U0001f9e0 Reflection Candidates: {len(entries)} valid / {total} total"
            )
            if skipped_context:
                print(f"- Skipped {skipped_context} context mismatch")
            if skipped_low:
                print(f"- Skipped {skipped_low} low importance")
            if skipped_missing:
                print(f"- Skipped {skipped_missing} missing transcript")
            if skipped_junk:
                print(f"- Skipped {skipped_junk} junk transcripts")
            for e in entries:
                tag = e.bookmark_label or e.type or ""
                preview = (e.summary or e.event).splitlines()[0][:80]
                print(f"- [{tag}] {e.created_at:%Y-%m-%d} — {preview}...")

        return entries

    def reflect_on_recent_activity(self) -> AssistantReflectionLog | None:
        """Run a reflection using the assistant's default memory context."""
        if not self.assistant.memory_context:
            logger.debug(
                "[ReflectionEngine] Skipping reflection for %s; no memory context",
                self.assistant.slug,
            )
            return None
        return self.reflect_now()

    def build_reflection_prompt(self, memories: list[str]) -> str:
        joined_memories = "\n".join(memories)
        return f"""You are {self.assistant.name}, an AI assistant with reflective capabilities.

    Below are some recent memory entries. Reflect on them and identify key patterns, changes in behavior, emerging goals, or important facts.

    Use 3–6 thoughtful bullet points to summarize your reflections.

    Memories:
    \"\"\"
    {joined_memories}
    \"\"\"

    Was your tone appropriate for the tasks assigned?
    Would a different emotional state have produced better results?
    """

    def get_reflection_system_prompt(self) -> str:
        """Return the system prompt content for reflections, creating a fallback if missing."""
        slug = "reflection-prompt"
        try:
            prompt = Prompt.objects.get(slug=slug)
            return prompt.content
        except Prompt.DoesNotExist:
            fallback = (
                "You are an AI assistant reflecting on memory. "
                "Extract useful patterns and summarize insights."
            )
            prompt, _ = Prompt.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": "Reflection Prompt",
                    "type": "system",
                    "content": fallback,
                    "source": "fallback",
                    "token_count": count_tokens(fallback),
                },
            )
            logger.warning(
                "[ReflectionEngine] Created fallback prompt for slug %s", slug
            )
            return prompt.content

    def generate_reflection(
        self,
        prompt: str,
        temperature: float = 0.5,
        rag_chunks: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        glossary_override: Optional[dict[str, str]] = None,
    ) -> str:
        from utils.llm_router import call_llm

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if rag_chunks:
            messages.append(
                {
                    "role": "system",
                    "content": "You are a retrieval-aware assistant. Always use the provided document context. Do not guess or hallucinate.",
                }
            )
            lines = ["You must use only the following context to answer:", ""]
            for i, text in enumerate(rag_chunks, 1):
                lines.append(f'[Chunk {i}] "{text[:200]}"')
            messages.append({"role": "system", "content": "\n".join(lines)})
        if glossary_override:
            import json
            messages.append(
                {
                    "role": "system",
                    "content": json.dumps({"glossary": glossary_override}),
                }
            )
        messages.append({"role": "user", "content": prompt})
        logger.debug("Reflection messages: %s", messages)
        return call_llm(
            messages,
            model=self.assistant.preferred_model or "gpt-4o",
            temperature=temperature,
            max_tokens=400,
        )

    def reflect_now(
        self,
        *,
        scene: str | None = None,
        location_context: str | None = None,
        verbose: bool = False,
    ) -> AssistantReflectionLog | None:
        """Run a quick reflection over recent memories for the assistant's context."""
        if not self.assistant.memory_context:
            logger.debug(
                "[ReflectionEngine] Skipping reflection for %s; no memory context",
                self.assistant.slug,
            )
            return None

        context = self.context
        entries = self.get_memory_entries(limit=30, verbose=verbose)
        texts = [e.summary or e.event for e in entries if (e.summary or e.event)]
        if not texts:
            logger.info(
                "[ReflectionEngine] No memory entries for context %s", context.id
            )
            try:
                tag, _ = Tag.objects.get_or_create(
                    slug="pending-reflection", defaults={"name": "pending-reflection"}
                )
                context.tags.add(tag)
            except Exception:
                logger.exception("Failed to tag context for later reflection")
            return None

        from assistants.utils.chunk_retriever import get_relevant_chunks

        query_text = texts[0] if texts else context.content or ""
        chunk_info, *_ = get_relevant_chunks(
            str(self.assistant.id),
            query_text,
            memory_context_id=str(self.assistant.memory_context_id)
            if self.assistant.memory_context_id
            else None,
            only_trusted=self.assistant.require_trusted_anchors,
        )
        rag_chunks = [c["text"] for c in chunk_info]
        if scene or location_context:
            loc_parts = []
            if scene:
                loc_parts.append(f"Scene: {scene}")
            if location_context:
                loc_parts.append(location_context)
            texts.insert(0, " | ".join(loc_parts))

        prompt = None
        if texts:
            prompt = self.build_reflection_prompt(texts)

        try:
            system_prompt = self.get_reflection_system_prompt()
            reflection_text = (
                self.generate_reflection(
                    prompt,
                    rag_chunks=rag_chunks,
                    system_prompt=system_prompt,
                )
                if prompt
                else "No meaningful content."
            )

            log = AssistantReflectionLog.objects.create(
                assistant=self.assistant,
                project=self.project,
                title=f"Reflection for context {context.id}",
                summary=reflection_text,
                raw_prompt=prompt,
            )
            usage = log_prompt_usage(
                prompt_slug="reflection-prompt",
                prompt_title="Reflection Prompt",
                used_by="assistant_reflection",
                context_id=str(context.id),
                rendered_prompt=prompt or "",
                assistant_id=str(self.assistant.id),
                assistant_slug=self.assistant.slug,
            )
            if usage:
                log.prompt_log = usage
                log.save(update_fields=["prompt_log"])

            mem = MemoryEntry.objects.create(
                event=reflection_text,
                assistant=self.assistant,
                source_role="assistant",
                linked_content_type=ContentType.objects.get_for_model(self.assistant),
                linked_object_id=self.assistant.id,
                is_conversation=False,
                context=context,
            )

            emb = generate_embedding(reflection_text)
            if emb:
                save_embedding(log, emb)

            chunk_ids = [c.get("chunk_id") for c in chunk_info if c.get("chunk_id")]
            if chunk_ids:
                chunks = list(DocumentChunk.objects.filter(id__in=chunk_ids))
                log.related_chunks.set(chunks)
                mem.context_tags = [f"chunk:{cid}" for cid in chunk_ids]
                mem.save(update_fields=["context_tags"])
                tags = set()
                for ch in chunks:
                    tags.update(ch.tags or [])
                if tags:
                    insight = AssistantReflectionInsight.objects.create(
                        assistant=self.assistant,
                        linked_document=chunks[0].document,
                        text=reflection_text,
                    )
                    insight.chunks.set(chunks)
                    for name in tags:
                        tag, _ = Tag.objects.get_or_create(
                            name=name, defaults={"slug": slugify(name)}
                        )
                        insight.tags.add(tag)

            entry = SwarmMemoryEntry.objects.create(
                title=log.title,
                content=reflection_text,
                origin="reflection",
            )
            entry.linked_agents.set(self.assistant.assigned_agents.all())
            if self.project:
                entry.linked_projects.add(self.project)

            if scene:
                AssistantThoughtLog.objects.create(
                    assistant=self.assistant,
                    thought=f"Location {scene} considered during reflection",
                    thought_type="scene_match",
                    origin="automatic",
                )

            logger.info(f"[🧠] Reflection saved for context {context.id}.")
            return log
        except Exception as e:
            logger.error(f"[❌] Reflection failed: {e}", exc_info=True)
            raise

    @staticmethod
    def get_reflection_assistant():
        slug = slugify("Reflection Engine")
        assistant, created = Assistant.objects.get_or_create(
            slug=slug,
            defaults={
                "name": "Reflection Engine",
                "description": "Analyzes DevDocs and reflects on system evolution.",
                "specialty": "assistant_reflection",
                "tone": "analytical",
                "preferred_model": "ollama:mistral",
            },
        )
        if created:
            from assistants.utils.assistant_lookup import log_cli_assistant_event

            log_cli_assistant_event("get_reflection_assistant", assistant, True)
            print(f"✅ Created Assistant: {assistant.name}")
        return assistant

    @staticmethod
    def get_or_create_project(assistant):
        """Return the assistant's reflection project, creating one if needed."""
        project, _ = AssistantProject.objects.get_or_create(
            assistant=assistant,
            title="System Reflection",
            defaults={
                "description": "Ongoing reflections on code and architecture evolution.",
            },
        )
        return project

    def reflect_on_document(self, document):
        """Reflect on a Document or DevDoc instance and save insights.

        Returns a tuple ``(summary, insights, prompt)`` where ``prompt`` is the
        generated ``Prompt`` instance or ``None``.
        """

        # Allow passing a DevDoc; use its linked Document
        if isinstance(document, DevDoc):
            if not document.linked_document:
                raise ValueError(f"DevDoc '{document.title}' has no linked Document")
            target_document = document.linked_document
        else:
            target_document = document

        logger.info(
            f"[ReflectionEngine] Reflecting on document: {target_document.title}"
        )

        # Tag fallback-prone anchors present in the document
        try:
            from memory.models import AnchorConfidenceLog, SymbolicMemoryAnchor
            from intel_core.utils.glossary_tagging import _match_anchor

            bad_logs = AnchorConfidenceLog.objects.filter(
                assistant=self.assistant, fallback_rate__gte=0.3
            )
            suspect = SymbolicMemoryAnchor.objects.filter(
                id__in=bad_logs.values_list("anchor_id", flat=True)
            )
            tagged = []
            for anc in suspect:
                found, _ = _match_anchor(anc, target_document.content)
                if found:
                    tag, _ = Tag.objects.get_or_create(
                        slug=anc.slug, defaults={"name": anc.label}
                    )
                    if not target_document.tags.filter(id=tag.id).exists():
                        target_document.tags.add(tag)
                        tagged.append(anc.slug)
            if tagged:
                logger.info(
                    f"[ReflectionEngine] Auto-tagged fallback anchors: {tagged}"
                )
        except Exception:
            logger.exception("Failed to auto-tag fallback anchors")

        # Placeholder reflection logic (replace with your actual logic)
        summary = f"Auto-generated summary for {target_document.title}"
        insights = [
            f"Insight 1 about {target_document.title}",
            f"Insight 2 about {target_document.title}",
        ]

        # Save insights
        for insight in insights:
            AssistantReflectionInsight.objects.create(
                assistant=self.assistant,
                linked_document=target_document,
                text=insight,
            )

        prompt_obj = None
        if summary:
            prompt_text = generate_prompt_from_summary(summary)
            if prompt_text:
                prompt_obj, _ = Prompt.objects.get_or_create(
                    assistant=self.assistant,
                    source_document=target_document,
                    source="reflection",
                    defaults={
                        "title": f"Reflection Prompt - {target_document.title}"[:255],
                        "content": prompt_text,
                        "type": "assistant",
                        "tone": "informative",
                        "token_count": count_tokens(prompt_text),
                    },
                )
                for name in ["rag", "document", "summary"]:
                    tag, _ = Tag.objects.get_or_create(
                        name=name, defaults={"slug": slugify(name)}
                    )
                    prompt_obj.tags.add(tag)

                linked_project = (
                    self.assistant.current_project.linked_projects.first()
                    if self.assistant.current_project
                    else None
                )
                if linked_project:
                    AssistantPromptLink.objects.get_or_create(
                        project=linked_project, prompt=prompt_obj
                    )

                if not self.assistant.system_prompt:
                    self.assistant.system_prompt = prompt_obj
                    self.assistant.save(update_fields=["system_prompt"])

        # Save reflection log and memory entry
        log = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            document=target_document,
            title=f"Reflection on {target_document.title}",
            summary=summary or "",
            raw_prompt=prompt_text or "",
        )

        mem = MemoryEntry.objects.create(
            event=summary or "",
            assistant=self.assistant,
            source_role="assistant",
            is_conversation=False,
            context=self.assistant.memory_context,
            document=target_document,
        )

        log.linked_memory = mem
        log.save(update_fields=["linked_memory"])

        target_document.last_reflected_at = timezone.now()
        target_document.save(update_fields=["last_reflected_at"])

        from assistants.tasks import run_rag_ci_checks
        run_rag_ci_checks.delay(self.assistant.slug)

        return summary, insights, prompt_obj

    def reflect_on_memory(self, memory: MemoryEntry) -> AssistantReflectionLog | None:
        """
        Create a reflection log for a single memory entry.
        """
        if not memory or not memory.event.strip():
            return None

        prompt = f"""You are {self.assistant.name}, an AI assistant with reflective capabilities.

    Below is a memory entry.

    Reflect on it and summarize the insight in 2–4 thoughtful bullet points.

    Memory:
    \"\"\"
    {memory.event.strip()}
    \"\"\""""

        try:
            system_prompt = self.get_reflection_system_prompt()
            reflection_text = self.generate_reflection(
                prompt, system_prompt=system_prompt
            )

            log = AssistantReflectionLog.objects.create(
                project=self.project,
                assistant=self.assistant,
                linked_memory=memory,
                title=f"Reflection on memory {memory.id}",
                summary=reflection_text,
                raw_prompt=prompt,
                category="meta",
            )
            usage = log_prompt_usage(
                prompt_slug="memory-reflection",
                prompt_title="Memory Reflection",
                used_by="assistant_reflection",
                context_id=str(memory.context_id or ""),
                rendered_prompt=prompt,
                assistant_id=str(self.assistant.id),
                assistant_slug=self.assistant.slug,
            )
            if usage:
                log.prompt_log = usage
                log.save(update_fields=["prompt_log"])

            logger.info(f"[✅] Reflection log created for memory {memory.id}")
            return log
        except Exception as e:
            logger.error(
                f"[❌] Failed to reflect on memory {memory.id}: {e}", exc_info=True
            )
            return None

    def reflect_on_assistant(
        self, assistant: Assistant, project: AssistantProject
    ) -> AssistantReflectionLog:
        """Generate a reflection about a newly spawned assistant."""
        prompt = f"""You are {self.assistant.name}, reflecting on a delegated assistant you created.\n\n" \
                f"Assistant Name: {assistant.name}\n" \
                f"Specialty: {assistant.specialty or '(unspecified)'}\n" \
                f"Description: {assistant.description or '(none)'}\n" \
                "Provide constructive feedback on its purpose, tone, and any improvements."\
                "\nWas your tone appropriate for the tasks assigned?"\
                "\nWould a different emotional state have produced better results?"""
        system_prompt = self.get_reflection_system_prompt()
        reflection_text = self.generate_reflection(
            prompt, system_prompt=system_prompt
        )
        log = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=project,
            summary=reflection_text,
            raw_prompt=prompt,
            title=f"Reflection on assistant {assistant.name}",
        )
        usage = log_prompt_usage(
            prompt_slug="assistant-reflection",
            prompt_title="Assistant Reflection",
            used_by="assistant_reflection",
            context_id=str(project.memory_context_id if project else ""),
            rendered_prompt=prompt,
            assistant_id=str(self.assistant.id),
            assistant_slug=self.assistant.slug,
        )
        if usage:
            log.prompt_log = usage
            log.save(update_fields=["prompt_log"])
        return log

    # CODEx MARKER: plan_from_thread_context


def plan_from_thread_context(
    self,
    thread: "NarrativeThread",
    assistant: Assistant,
    project: AssistantProject | None = None,
):
    """Generate next actions from a narrative thread."""
    from agents.utils.agent_controller import AgentController
    from assistants.models import AssistantObjective, AssistantNextAction
    from utils.llm_router import call_llm

    project = project or self.get_or_create_project(assistant)
    objective = (
        AssistantObjective.objects.filter(project=project, assistant=assistant)
        .order_by("created_at")
        .first()
    )
    if not objective:
        objective = AssistantObjective.objects.create(
            project=project,
            assistant=assistant,
            title=f"Thread: {thread.title}",
            description=thread.summary or "",
        )

    summary = thread.continuity_summary or thread.summary or thread.title
    prompt = (
        f"You are planning actions for the thread '{thread.title}'. "
        f"Context: {summary}\n"
        "List 3 to 5 short actionable next steps."
    )
    try:
        output = call_llm(
            [{"role": "user", "content": prompt}],
            model=assistant.preferred_model or "gpt-4o",
            temperature=0.4,
            max_tokens=300,
        )
    except Exception as e:
        logger.error(f"plan_from_thread_context failed: {e}")
        output = "- Review recent memories\n- Clarify goals"

    lines = [l.strip("- •\t ") for l in output.splitlines() if l.strip()]
    lines = [l for l in lines if l][:5]
    controller = AgentController()
    actions = []
    for idx, line in enumerate(lines):
        agent = controller.recommend_agent_for_task(line, thread)
        action = AssistantNextAction.objects.create(
            objective=objective,
            content=line,
            assigned_agent=agent,
            linked_thread=thread,
            importance_score=max(0.0, 1.0 - idx * 0.1),
        )
        actions.append(action)
    return actions


def evaluate_thought_continuity(
    self, *, project: AssistantProject | None = None
) -> dict:
    """Assess continuity of recent thoughts and suggest next actions."""

    qs = AssistantThoughtLog.objects.filter(assistant=self.assistant)
    if project:
        qs = qs.filter(project=project)

    recent = list(qs.order_by("-created_at")[:5])
    if not recent:
        return {
            "continuity_score": 1.0,
            "recent_thoughts": [],
            "suggestions": [],
        }

    expected_thread = None
    if project:
        expected_thread = project.thread or project.narrative_thread
    if not expected_thread:
        expected_thread = recent[0].narrative_thread

    total = len(recent)
    aligned = sum(
        1
        for t in recent
        if t.narrative_thread_id == getattr(expected_thread, "id", None)
    )
    score = aligned / total if total else 1.0

    suggestions = []
    if score < 0.6:
        suggestions.append("review recent events and reconnect to the main thread")

    return {
        "continuity_score": round(score, 2),
        "recent_thoughts": [
            {
                "id": str(t.id),
                "text": t.thought,
                "thread": str(t.narrative_thread_id) if t.narrative_thread_id else None,
            }
            for t in recent
        ],
        "thread_id": str(expected_thread.id) if expected_thread else None,
        "suggestions": suggestions,
    }


# codex-coach:assign-training
def assign_training_documents(
    assistant: Assistant, agent: "Agent", docs: list["Document"], train: bool = True
) -> list["AgentTrainingAssignment"]:
    """Assign documents to an agent and optionally trigger training."""
    from agents.models import AgentTrainingAssignment
    from agents.utils.agent_controller import train_agent_from_documents

    assignments = []
    for doc in docs:
        assignment = AgentTrainingAssignment.objects.create(
            assistant=assistant,
            agent=agent,
            document=doc,
        )
        assignments.append(assignment)

    if train and docs:
        result = train_agent_from_documents(agent, list(docs))
        AgentTrainingAssignment.objects.filter(
            id__in=[a.id for a in assignments]
        ).update(completed=True, completed_at=timezone.now())
        logger.info(
            f"[Training] Agent {agent.name} trained on {len(docs)} documents: {result}"
        )

    return assignments


# codex-coach:evaluate-training
def evaluate_agent_training(assistant: Assistant, agent: "Agent") -> dict:
    """Summarize training progress and return readiness report."""
    from agents.models import AgentTrainingAssignment, AgentFeedbackLog

    assignments = AgentTrainingAssignment.objects.filter(
        agent=agent, assistant=assistant
    )
    completed = assignments.filter(completed=True).count()
    pending = assignments.filter(completed=False).count()
    feedback_scores = list(
        AgentFeedbackLog.objects.filter(agent=agent, score__isnull=False).values_list(
            "score", flat=True
        )
    )
    avg_score = sum(feedback_scores) / len(feedback_scores) if feedback_scores else None

    tags = set(agent.tags or [])
    skills = set(_skill_names(agent.verified_skills))

    report = {
        "completed_assignments": completed,
        "pending_assignments": pending,
        "avg_feedback": avg_score,
        "skills": list(skills),
        "tags": list(tags),
    }

    if avg_score is not None and avg_score < 0.5:
        report["next_steps"] = "Increase targeted practice on low-scoring areas"
    elif pending:
        report["next_steps"] = "Complete pending training assignments"
    else:
        report["next_steps"] = "Agent ready for advanced tasks"

    return report


def reflect_on_agent_network(assistant: Assistant) -> str:
    """Generate a reflection on the assistant's agent network."""
    from utils.llm_router import call_llm

    agents = list(assistant.assigned_agents.all())
    snapshot_lines = []
    for a in agents:
        assignments = AgentTrainingAssignment.objects.filter(agent=a).count()
        feedback = AgentFeedbackLog.objects.filter(
            agent=a, score__isnull=False
        ).order_by("-created_at")[:3]
        avg = sum(f.score for f in feedback) / len(feedback) if feedback else 0.0
        snapshot_lines.append(
            f"{a.name}: {assignments} trainings, avg feedback {avg:.2f}"
        )

    context = "\n".join(snapshot_lines)
    prompt = f"""### Assistant Agent Reflection

You are {assistant.name}, supervising a network of agents.

Based on the latest training assignments, feedback logs, and the shared skill graph, reflect on the following:

- Which agents have improved the most?
- Are there skill gaps or overlaps?
- Which agents are underutilized or overloaded?
- Suggest any skill clusters or role specializations.
- Recommend new training paths or delegation strategies.

Agents snapshot:\n{context}\n\nReturn a markdown summary in 4-6 bullet points."""

    try:
        return call_llm(
            [{"role": "user", "content": prompt}],
            model=assistant.preferred_model or "gpt-4o",
            temperature=0.4,
        )
    except Exception:
        return "- Unable to generate reflection."


def reflect_on_agent_swarm(assistant: Assistant) -> AssistantReflectionLog:
    """
    Reflects on both agent-cluster evolution and mentoring/swarm dynamics,
    then logs the insight as an AssistantReflectionLog.
    """
    from utils.llm_router import call_llm

    # 1) Build cluster context
    clusters = AgentCluster.objects.filter(
        agents__parent_assistant=assistant
    ).distinct()
    cluster_lines = [
        f"{c.name} ({c.agents.count()} agents) – {c.purpose}" for c in clusters
    ]
    cluster_context = "\n".join(cluster_lines) or "No clusters defined."

    # 2) Build mentoring/swarm context
    agents = list(assistant.assigned_agents.all())
    if agents:
        mentoring_entries = MemoryEntry.objects.filter(
            linked_agents__in=agents, tags__name__iexact="mentoring"
        ).order_by("-created_at")[:20]
        # Interaction bullet points
        interaction_lines = [f"- {m.event}" for m in mentoring_entries] or [
            "- No mentoring interactions."
        ]
        # Per-agent metrics
        agent_metrics = []
        for a in agents:
            taught = sum(1 for m in mentoring_entries if m.event.startswith(a.name))
            learned = sum(1 for m in mentoring_entries if f"taught {a.name}" in m.event)
            agent_metrics.append(f"{a.name}: taught {taught}, learned {learned}")
        mentoring_context = "\n".join(agent_metrics + [""] + interaction_lines)
    else:
        mentoring_context = "No agents assigned."

    # 3) Compose the combined prompt
    prompt = (
        f"### Agent Swarm & Cluster Reflection\n\n"
        f"You are {assistant.name}, overseeing a network of AI agents.\n\n"
        f"**Clusters:**\n{cluster_context}\n\n"
        f"**Mentoring & Interactions:**\n{mentoring_context}\n\n"
        "Please cover:\n"
        "- Which clusters have grown or dissolved?\n"
        "- Are any roles redundant or missing?\n"
        "- Which agents are mentoring vs being mentored?\n"
        "- Propose spawn, merge, repurpose, or retraining actions.\n\n"
        "Respond with 4–6 concise bullet points."
    )

    # 4) Call the LLM and log the result
    summary = call_llm(
        [{"role": "user", "content": prompt}],
        model=assistant.preferred_model or "gpt-4o",
        temperature=0.4,
    )


def reflect_on_agent_swarm(assistant: Assistant) -> AssistantReflectionLog:
    """
    Reflects on both agent‐cluster evolution and mentoring/swarm dynamics,
    then logs the insight as an AssistantReflectionLog.
    """
    from utils.llm_router import call_llm

    # 1) Cluster context
    clusters = AgentCluster.objects.filter(
        agents__parent_assistant=assistant
    ).distinct()
    cluster_lines = [
        f"{c.name} ({c.agents.count()} agents) – {c.purpose}" for c in clusters
    ]
    cluster_context = "\n".join(cluster_lines) or "No clusters defined."

    # 2) Mentoring/swarm context
    agents = list(assistant.assigned_agents.all())
    if agents:
        mentoring_entries = MemoryEntry.objects.filter(
            linked_agents__in=agents, tags__name__iexact="mentoring"
        ).order_by("-created_at")[:20]
        interaction_lines = [f"- {m.event}" for m in mentoring_entries] or [
            "- No mentoring interactions."
        ]
        agent_metrics = []
        for a in agents:
            taught = sum(1 for m in mentoring_entries if m.event.startswith(a.name))
            learned = sum(1 for m in mentoring_entries if f"taught {a.name}" in m.event)
            agent_metrics.append(f"{a.name}: taught {taught}, learned {learned}")
        mentoring_context = "\n".join(agent_metrics + [""] + interaction_lines)
    else:
        mentoring_context = "No agents assigned."

    # 3) Build prompt
    prompt = (
        f"### Agent Swarm & Cluster Reflection\n\n"
        f"You are {assistant.name}, overseeing a network of AI agents.\n\n"
        f"**Clusters:**\n{cluster_context}\n\n"
        f"**Mentoring & Interactions:**\n{mentoring_context}\n\n"
        "Please cover:\n"
        "- Which clusters have grown or dissolved?\n"
        "- Are any roles redundant or missing?\n"
        "- Which agents are mentoring vs being mentored?\n"
        "- Propose spawn, merge, repurpose, or retraining actions.\n\n"
        "Respond with 4–6 concise bullet points."
    )

    summary = call_llm(
        [{"role": "user", "content": prompt}],
        model=assistant.preferred_model or "gpt-4o",
        temperature=0.4,
    )

    log = AssistantReflectionLog.objects.create(
        assistant=assistant,
        title="Agent Swarm & Cluster Reflection",
        summary=summary,
    )
    usage = log_prompt_usage(
        prompt_slug="agent-swarm-reflection",
        prompt_title="Agent Swarm Reflection",
        used_by="assistant_reflection",
        rendered_prompt=prompt,
        assistant_id=str(assistant.id),
        assistant_slug=assistant.slug,
    )
    if usage:
        log.prompt_log = usage
        log.save(update_fields=["prompt_log"])
    return log


def suggest_agent_resurrections(assistant: Assistant) -> list[str]:
    """
    Looks for recently‐archived agents with strong skills and logs suggestions.
    Returns markdown bullets like:
      - **AgentName** – skill **SkillName** (0.85)
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    archived = Agent.objects.filter(
        parent_assistant=assistant, is_active=False
    ).exclude(reactivated_at__gte=thirty_days_ago)

    bullets: list[str] = []
    for agent in archived:
        link = (
            AgentSkillLink.objects.filter(agent=agent, strength__gte=0.6)
            .order_by("-strength")
            .first()
        )
        if not link:
            continue
        bullets.append(
            f"- **{agent.name}** – skill **{link.skill.name}** ({link.strength:.2f})"
        )

    if bullets:
        log = AssistantReflectionLog.objects.create(
            assistant=assistant,
            title="Agent Resurrection Suggestions",
            summary="\n".join(bullets),
        )
        usage = log_prompt_usage(
            prompt_slug="resurrection-suggestions",
            prompt_title="Agent Resurrection Suggestions",
            used_by="assistant_reflection",
            rendered_prompt="\n".join(bullets),
            assistant_id=str(assistant.id),
            assistant_slug=assistant.slug,
        )
        if usage:
            log.prompt_log = usage
            log.save(update_fields=["prompt_log"])

    return bullets


def forecast_future_swarm_needs(assistant: Assistant) -> str:
    """Reflect on temporal analytics and recommend future swarm actions."""
    from utils.llm_router import call_llm

    report = generate_temporal_swarm_report()
    prompt = (
        f"### Swarm Temporal Report\n{json.dumps(report, indent=2)}\n\n"
        "Based on this data, outline recommendations for:\n"
        "- New training paths\n"
        "- Archetype mutations\n"
        "- Cluster merging or splitting\n"
        "- Retiring agents gracefully"
    )
    try:
        forecast = call_llm(
            [{"role": "user", "content": prompt}],
            model=assistant.preferred_model or "gpt-4o",
            temperature=0.3,
            max_tokens=400,
        )
    except Exception:
        forecast = "Unable to generate forecast."

    log = AssistantReflectionLog.objects.create(
        assistant=assistant,
        title="Swarm Forecast",
        summary=forecast,
    )
    usage = log_prompt_usage(
        prompt_slug="swarm-forecast",
        prompt_title="Swarm Forecast",
        used_by="assistant_reflection",
        rendered_prompt=prompt,
        assistant_id=str(assistant.id),
        assistant_slug=assistant.slug,
    )
    if usage:
        log.prompt_log = usage
        log.save(update_fields=["prompt_log"])
    entry = SwarmMemoryEntry.objects.create(
        title="Swarm Forecast",
        content=forecast,
        origin="forecast",
    )
    entry.linked_agents.set(assistant.assigned_agents.all())
    return forecast


def reflect_on_tools(assistant: Assistant) -> AssistantReflectionLog | None:
    """Summarize currently assigned tools."""
    from assistants.models.tooling import AssistantToolAssignment

    assignments = AssistantToolAssignment.objects.filter(assistant=assistant)
    if not assignments:
        return None

    lines = []
    for a in assignments:
        tag_names = ", ".join(t.name for t in a.tool.tags.all())
        lines.append(
            f"- {a.tool.name}: {a.reason or 'n/a'} (score {a.confidence_score:.2f})"
            + (f" Tags: {tag_names}" if tag_names else "")
        )

    summary = "\n".join(lines)
    log = AssistantReflectionLog.objects.create(
        assistant=assistant,
        title="Tool Reflection",
        summary=summary,
    )
    assignments.update(reflection_log=log)
    return log


def reflect_on_dissent_signals(assistant: Assistant) -> str:
    """Aggregate dissent logs and propose realignment actions."""
    logs = (
        AgentFeedbackLog.objects.filter(is_dissent=True)
        .select_related("agent")
        .order_by("-created_at")[:20]
    )
    if logs:
        lines = [
            f"- {log.agent.name}: {log.dissent_reason or log.feedback_text}"
            for log in logs
        ]
        summary = "\n".join(lines)
    else:
        summary = "No dissent signals detected."

    log = AssistantReflectionLog.objects.create(
        assistant=assistant,
        title="Dissent Review",
        summary=summary,
    )
    usage = log_prompt_usage(
        prompt_slug="dissent-review",
        prompt_title="Dissent Review",
        used_by="assistant_reflection",
        rendered_prompt=summary,
        assistant_id=str(assistant.id),
        assistant_slug=assistant.slug,
    )
    if usage:
        log.prompt_log = usage
        log.save(update_fields=["prompt_log"])
    entry = SwarmMemoryEntry.objects.create(
        title="Dissent Review",
        content=summary,
        origin="dissent_review",
    )
    entry.linked_agents.set([log.agent for log in logs])
    from mcp_core.models import Tag
    from django.utils.text import slugify

    tags = []
    for name in ["dissent", "realignment", "resistance"]:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
        tags.append(tag)
    entry.tags.set(tags)

    return summary


def reflect_on_tool_usage(assistant: Assistant) -> list["ToolReflectionLog"]:
    """Generate reflections on tool usage grouped by tool."""
    from tools.models import ToolExecutionLog, ToolReflectionLog
    from mcp_core.models import Tag
    from django.utils.text import slugify

    logs = ToolExecutionLog.objects.filter(assistant=assistant).order_by("-created_at")[:200]
    grouped: dict[int, list[ToolExecutionLog]] = {}
    for log in logs:
        grouped.setdefault(log.tool_id, []).append(log)

    reflections = []
    for tool_id, items in grouped.items():
        tool = items[0].tool
        success_rate = sum(1 for i in items if i.success) / len(items)
        summary = f"Used {len(items)} times with {success_rate:.0%} success."
        if success_rate < 0.5:
            summary += " Needs improvement."
            tag_name = "misuse"
        else:
            tag_name = "efficiency"

        ref = ToolReflectionLog.objects.create(
            tool=tool,
            assistant=assistant,
            execution_log=items[0],
            reflection=summary,
            confidence_score=success_rate,
        )
        tag, _ = Tag.objects.get_or_create(name=tag_name, defaults={"slug": slugify(tag_name)})
        ref.insight_tags.add(tag)
        reflections.append(ref)
    return reflections
