from typing import List
from memory.models import MemoryChain, MemoryEntry
from mcp_core.models import NarrativeThread


def get_linked_chains(thread: NarrativeThread) -> List[MemoryChain]:
    """Return all chains linked to a thread ordered by creation."""
    return list(MemoryChain.objects.filter(thread=thread).order_by("created_at"))


def recall_from_thread(chain: MemoryChain) -> List[MemoryEntry]:
    """Gather relevant memories from all chains sharing the same thread."""
    if not chain.thread:
        return list(chain.memories.all().order_by("-created_at"))

    sibling_chains = MemoryChain.objects.filter(thread=chain.thread)
    entries = (
        MemoryEntry.objects.filter(chains__in=sibling_chains)
        .distinct()
        .prefetch_related("tags")
        .order_by("-created_at")
    )

    tag_set = set(chain.context_tags or [])

    def score(mem: MemoryEntry):
        overlap = len(tag_set.intersection({t.slug for t in mem.tags.all()}))
        return (overlap, mem.created_at)

    return sorted(entries, key=score, reverse=True)
