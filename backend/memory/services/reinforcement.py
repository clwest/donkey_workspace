from typing import Optional
from mcp_core.models import Tag
from memory.models import (
    MemoryEntry,
    SymbolicMemoryAnchor,
    AnchorReinforcementLog,
)

REINFORCEMENT_THRESHOLD = 0.65

__all__ = [
    "reinforce_glossary_anchor",
    "anchor_reinforcement_log",
    "REINFORCEMENT_THRESHOLD",
]


def anchor_reinforcement_log(
    anchor: SymbolicMemoryAnchor,
    assistant=None,
    memory: Optional[MemoryEntry] = None,
    reason: str = "",
    score: float = 0.0,
    *,
    trigger_source: str = "manual",
    outcome: str = "match",
    score_delta: float = 0.0,
) -> AnchorReinforcementLog:
    return AnchorReinforcementLog.objects.create(
        anchor=anchor,
        assistant=assistant,
        memory=memory,
        reason=reason,
        trigger_source=trigger_source,
        outcome=outcome,
        score=score,
        score_delta=score_delta,
    )


def reinforce_glossary_anchor(
    anchor: SymbolicMemoryAnchor,
    *,
    assistant=None,
    source: str = "retrieval_match",
    score: float = 0.0,
    outcome: str = "match",
    score_delta: float = 0.0,
) -> MemoryEntry:
    summary = f"{anchor.label} reinforced via {source}"
    mem = MemoryEntry.objects.create(
        assistant=assistant,
        summary=summary,
        anchor=anchor,
        triggered_by=f"anchor_reinforcement:{source}",
        context=anchor.memory_context,
        type="reinforcement",
    )
    gtag, _ = Tag.objects.get_or_create(slug="glossary", defaults={"name": "glossary"})
    rtag, _ = Tag.objects.get_or_create(
        slug="reinforcement", defaults={"name": "reinforcement"}
    )
    mem.tags.add(gtag, rtag)
    anchor_reinforcement_log(
        anchor,
        assistant=assistant,
        memory=mem,
        reason=source,
        trigger_source=source,
        outcome=outcome,
        score=score,
        score_delta=score_delta,
    )
    if assistant and not anchor.reinforced_by.filter(id=assistant.id).exists():
        anchor.reinforced_by.add(assistant)
    return mem
