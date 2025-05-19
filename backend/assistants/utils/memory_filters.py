from assistants.models import AssistantMemoryChain
from memory.models import MemoryEntry


def get_filtered_memories(chain: AssistantMemoryChain):
    """Return memories filtered by tag and type settings."""
    qs = chain.memories.all()
    if chain.filter_tags.exists():
        qs = qs.filter(tags__in=chain.filter_tags.all()).distinct()
    if chain.exclude_types:
        qs = qs.exclude(type__in=chain.exclude_types)
    return qs.order_by("-created_at")
