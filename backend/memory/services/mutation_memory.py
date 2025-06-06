from typing import Optional

from mcp_core.models import Tag
from ..models import MemoryEntry, SymbolicMemoryAnchor

__all__ = ["generate_mutation_memory_entry"]


def generate_mutation_memory_entry(
    anchor: SymbolicMemoryAnchor,
    assistant,
    *,
    original_label: Optional[str] = None,
) -> Optional[MemoryEntry]:
    """Create a memory entry describing an applied glossary mutation."""
    if not assistant:
        return None

    old_label = original_label or anchor.label
    new_label = anchor.label
    source = anchor.mutation_source or "assistant_memory_inferred"
    summary = (
        f"I updated my glossary entry for {old_label} to {new_label} based on {source}. "
        "This should help me recall the concept more accurately."
    )

    mem = MemoryEntry.objects.create(
        assistant=assistant,
        anchor=anchor,
        context=anchor.memory_context,
        summary=summary,
        event=summary,
        triggered_by="glossary mutation applied",
        type="mutation",
        symbolic_change=False,
    )
    tag, _ = Tag.objects.get_or_create(
        slug="glossary-mutation", defaults={"name": "glossary-mutation"}
    )
    mem.tags.add(tag)
    return mem
