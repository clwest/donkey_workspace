from typing import Iterable

from .models import AssistantMemoryChain
from memory.models import MemoryEntry


def get_filtered_memories(chain: AssistantMemoryChain) -> Iterable[MemoryEntry]:
    """Return memories on the chain filtered by tags and types."""

    qs = MemoryEntry.objects.filter(chains=chain).order_by("-created_at")

    if chain.filter_tags.exists():
        qs = qs.filter(tags__in=chain.filter_tags.all()).distinct()

    if chain.exclude_types:
        qs = qs.exclude(type__in=chain.exclude_types)

    return qs[:20]
