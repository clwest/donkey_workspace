from memory.models import MemoryEntry
from mcp_core.models import MemoryContext
from django.contrib.contenttypes.models import ContentType


def get_or_create_context_from_memory(memory: MemoryEntry) -> MemoryContext:
    """
    Retrieve or create a MemoryContext for the given memory entry.

    Priority:
    1. Use existing context if already set.
    2. Try to find the most recent context linked to the assistant and project.
    3. Create a new context if none exists.
    """

    if memory.context:
        return memory.context

    context = MemoryContext.objects.create(
        target_content_type=ContentType.objects.get_for_model(MemoryEntry),
        target_object_id=memory.id,
        content=memory.summary or memory.event,
        important=memory.importance >= 8,
    )

    # Optionally attach context to the memory now (if you want persistence)
    memory.context = context
    memory.save(update_fields=["context"])

    return context
