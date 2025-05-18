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
