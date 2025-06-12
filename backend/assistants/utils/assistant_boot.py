from typing import Dict, List

from django.utils.timezone import now

from assistants.models import Assistant, AssistantBootLog
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.profile import AssistantUserProfile
from assistants.models.assistant import ChatSession
from intel_core.models import DocumentChunk
from mcp_core.models import MemoryContext, NarrativeThread
from memory.models import MemoryEntry


def generate_boot_profile(assistant: Assistant) -> Dict[str, object]:
    """Return a simplified boot profile for ``assistant``."""
    last_log = (
        AssistantBootLog.objects.filter(assistant=assistant)
        .order_by("-created_at")
        .first()
    )
    return {
        "has_system_prompt": bool(assistant.system_prompt),
        "has_memory_context": bool(assistant.memory_context),
        "has_preferred_model": bool(assistant.preferred_model),
        "last_tested_at": last_log.created_at if last_log else None,
    }


def run_assistant_self_test(assistant: Assistant) -> Dict[str, object]:
    """Run a basic self-test for ``assistant`` and record the result."""
    profile = generate_boot_profile(assistant)
    errors: List[str] = []

    if not profile["has_system_prompt"]:
        errors.append("Missing system prompt")
    if not profile["has_memory_context"]:
        errors.append("Missing memory context")
    if not profile["has_preferred_model"]:
        errors.append("Missing preferred model")

    passed = len(errors) == 0

    AssistantBootLog.objects.create(
        assistant=assistant,
        passed=passed,
        report="\n".join(errors),
    )

    return {"assistant": assistant.slug, "passed": passed, "errors": errors}


def run_batch_self_tests() -> List[Dict[str, object]]:
    """Run self-tests for all assistants and return their results."""
    results: List[Dict[str, object]] = []
    for a in Assistant.objects.all():
        results.append(run_assistant_self_test(a))
    return results


def boot_check(assistant: Assistant) -> Dict[str, object]:
    """Return boot status flags for the assistant."""
    has_context = bool(assistant.memory_context)
    has_intro_memory = MemoryEntry.objects.filter(
        assistant=assistant, type="assistant_intro"
    ).exists()
    has_origin_reflection = AssistantReflectionLog.objects.filter(
        assistant=assistant
    ).exists()
    has_profile = AssistantUserProfile.objects.filter(assistant=assistant).exists()
    has_narrative_thread = ChatSession.objects.filter(
        assistant=assistant, narrative_thread__isnull=False
    ).exists()
    has_custom_prompt = bool(
        assistant.system_prompt and assistant.system_prompt.slug != "generic"
    )
    rag_linked_docs = assistant.documents.count()
    chunks = DocumentChunk.objects.filter(document__linked_assistants=assistant)
    total_chunks = chunks.count()
    fallback_chunks = chunks.filter(chunk_type="fallback").count()
    short_chunks = chunks.filter(chunk_type="short").count()
    if total_chunks == 0:
        rag_chunk_health = "none"
    elif fallback_chunks == total_chunks:
        rag_chunk_health = "fallback-only"
    elif short_chunks == total_chunks:
        rag_chunk_health = "short-only"
    elif fallback_chunks == 0 and short_chunks == 0:
        rag_chunk_health = "all-good"
    else:
        rag_chunk_health = "mixed"

    return {
        "has_context": has_context,
        "has_intro_memory": has_intro_memory,
        "has_origin_reflection": has_origin_reflection,
        "has_profile": has_profile,
        "has_narrative_thread": has_narrative_thread,
        "has_custom_prompt": has_custom_prompt,
        "rag_linked_docs": rag_linked_docs,
        "rag_chunk_health": rag_chunk_health,
    }


def repair_assistant_boot(assistant: Assistant) -> list[str]:
    """Repair missing boot resources for ``assistant``."""
    changed: list[str] = []

    if not assistant.memory_context:
        assistant.memory_context = MemoryContext.objects.create(
            content=f"{assistant.name} context"
        )
        changed.append("memory_context")

    if not assistant.slug:
        assistant.slug = assistant.name.lower().replace(" ", "-")
        changed.append("slug")

    if not assistant.archetype:
        assistant.archetype = "debugger"
        changed.append("archetype")

    if changed:
        assistant.save(update_fields=changed)

    if assistant.created_by_id:
        profile, _ = AssistantUserProfile.objects.get_or_create(
            assistant=assistant, user=assistant.created_by
        )
        profile_changed = False
        if not profile.world:
            profile.world = "core"
            profile_changed = True
        if not profile.archetype:
            profile.archetype = assistant.archetype or "debugger"
            profile_changed = True
        if profile_changed:
            profile.save()
            changed.append("profile")

    if not MemoryEntry.objects.filter(
        assistant=assistant, type="assistant_intro"
    ).exists():
        MemoryEntry.objects.create(
            assistant=assistant,
            event="Welcome to the system",
            summary="Welcome to the system",
            type="assistant_intro",
            context=assistant.memory_context,
            source_role="assistant",
        )
        changed.append("welcome_memory")

    if not AssistantReflectionLog.objects.filter(assistant=assistant).exists():
        AssistantReflectionLog.objects.create(
            assistant=assistant, summary="Origin reflection"
        )
        changed.append("origin_reflection")

    sessions = ChatSession.objects.filter(
        assistant=assistant, narrative_thread__isnull=True
    )
    if sessions.exists():
        thread = NarrativeThread.objects.create(
            title=f"{assistant.name} Thread",
            created_by=assistant.created_by,
        )
        sessions.update(narrative_thread=thread, thread=thread)
        changed.append("narrative_thread")

    return changed
