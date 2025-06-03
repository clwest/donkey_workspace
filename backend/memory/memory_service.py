import logging
from typing import Iterable, Iterator, Union

from embeddings.helpers.helpers_io import save_embedding
from mcp_core.utils.auto_tag_from_embedding import auto_tag_from_embedding
from .models import MemoryEntry

logger = logging.getLogger("django")


class MemoryService:
    """Service layer for common memory operations."""

    def log_reflection(
        self, summary: Union[str, Iterator[str]], memories: Iterable[MemoryEntry]
    ):
        """Create an AssistantReflectionLog linked to the given memories."""
        from assistants.models import AssistantReflectionLog

        memories = list(memories)
        if not memories:
            raise ValueError("No memories provided")

        if not isinstance(summary, str):
            summary = "".join(list(summary))

        reflection = AssistantReflectionLog.objects.create(
            summary=summary,
            time_period_start=min(m.timestamp for m in memories),
            time_period_end=max(m.timestamp for m in memories),
        )
        reflection.linked_memories.set(memories)
        save_embedding(reflection, embedding=[])
        return reflection

    def auto_tag_memory_from_text(self, memory: MemoryEntry, text: str):
        """Auto-tag a memory using embedding-based suggestions."""
        from mcp_core.models import Tag

        if not text:
            return []

        tag_slugs = auto_tag_from_embedding(text) or []
        tag_objs = []
        for slug in tag_slugs:
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": slug})
            tag_objs.append(tag)
        if tag_objs:
            memory.tags.add(*tag_objs)
        return tag_objs

    def log_assistant_meta(self, assistant, message: str, linked_memory=None):
        """Log a meta thought for an assistant."""
        from assistants.helpers.logging_helper import log_assistant_thought

        log_assistant_thought(
            assistant,
            message,
            thought_type="meta",
            linked_memory=linked_memory,
        )

    def get_assistant_memories(self, slug: str):
        """Return assistant and its associated memories by slug."""
        from assistants.models import Assistant, AssistantThoughtLog

        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            return None, MemoryEntry.objects.none()

        linked_thought_ids = list(
            AssistantThoughtLog.objects.filter(assistant=assistant)
            .values_list("linked_memory_id", flat=True)
        )
        qs = MemoryEntry.objects.filter(assistant=assistant)
        if linked_thought_ids:
            qs = qs.union(MemoryEntry.objects.filter(id__in=linked_thought_ids))
        memories = qs.order_by("-created_at")
        return assistant, memories


_memory_service = None


def get_memory_service() -> MemoryService:
    """Get or create the singleton MemoryService instance."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
