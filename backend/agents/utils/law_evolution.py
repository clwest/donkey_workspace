from __future__ import annotations

from typing import Dict

from agents.models import SwarmCodex, SymbolicLawEntry, SwarmMemoryEntry
from mcp_core.models import Tag


def evolve_symbolic_law(codex: SwarmCodex) -> Dict:
    """Analyze codex laws and suggest updates."""
    active_count = codex.active_laws.count()
    drift_ratio = max(0.0, 1.0 - active_count / float(active_count + 5))

    summary = f"codex {codex.title} drift {drift_ratio:.2f}"

    entry = SwarmMemoryEntry.objects.create(
        title=f"Law Evolution for {codex.title}",
        content=summary,
        origin="law_evolution",
    )

    for label in ["law_evolution", "codex_update"]:
        tag, _ = Tag.objects.get_or_create(name=label, defaults={"slug": label})
        entry.tags.add(tag)

    return {"codex_id": codex.id, "drift_ratio": round(drift_ratio, 2), "memory_entry": entry.id}
