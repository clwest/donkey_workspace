# mcp_core/utils/thread_helpers.py

from mcp_core.models import NarrativeThread, MemoryContext
from django.db.models import Q
import logging

logger = logging.getLogger("threads")


def get_or_create_thread(
    title: str, description: str = "", tags: list = None
) -> NarrativeThread:
    """Fetch or create a narrative thread by title."""
    thread, created = NarrativeThread.objects.get_or_create(
        title=title.strip(), defaults={"description": description, "is_active": True}
    )
    if created:
        logger.info(f"🧵 Created new thread: {title}")
    if tags:
        thread.tags.set(tags)
    return thread


def attach_memory_to_thread(memory: MemoryContext, thread: NarrativeThread) -> None:
    """Link a memory to a narrative thread (additive)."""
    thread.memories.add(memory)
    thread.save()
    logger.info(f"🔗 Linked memory [{memory.id}] to thread [{thread.title}]")


def get_threads_for_memory(memory: MemoryContext):
    """Return all narrative threads linked to a memory."""
    return memory.narrative_threads.all()


def generate_thread_reflection(thread: NarrativeThread) -> str:
    """Summarize progress toward the thread's objective."""
    milestone_count = len(thread.milestones or [])
    objective = thread.long_term_objective or "No objective set"
    return f"Objective: {objective}\nMilestones tracked: {milestone_count}."


def generate_thread_refocus_prompt(thread: NarrativeThread) -> str:
    """Create a short prompt to help restore continuity for the thread."""
    objective = thread.long_term_objective or "(no objective)"
    summary = thread.summary or ""
    base = f"Let's refocus on the thread '{thread.title}'."
    return f"{base} Objective: {objective}. {summary}".strip()


def suggest_continuity(thread_id: str) -> dict:
    """Simple heuristic continuity analysis and link suggestions."""
    from django.utils import timezone

    thread = NarrativeThread.objects.get(id=thread_id)
    memories = list(thread.related_memories.all().order_by("-created_at")[:5])
    reflections = list(
        thread.thoughts.filter(thought_type="reflection").order_by("-created_at")[:5]
    )

    last_times = [m.created_at for m in memories]
    last_times += [r.created_at for r in reflections]
    last_activity = max(last_times) if last_times else None

    days_since = (timezone.now() - last_activity).days if last_activity else None
    summary_parts = [
        f"{len(memories)} memories",
        f"{len(reflections)} reflections",
    ]
    if days_since is not None:
        summary_parts.append(f"last activity {days_since}d ago")
    summary = ", ".join(summary_parts)

    similar = (
        NarrativeThread.objects.filter(tags__in=thread.tags.all())
        .exclude(id=thread.id)
        .distinct()[:3]
    )
    suggestions = [
        {
            "action": "link",
            "target_thread_id": str(t.id),
            "reason": "shared tags",
        }
        for t in similar
    ]

    thread.continuity_summary = summary
    thread.save(update_fields=["continuity_summary"])

    return {"continuity_summary": summary, "link_suggestions": suggestions}
