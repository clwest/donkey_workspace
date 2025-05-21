from __future__ import annotations

import json
from typing import Dict, List

from agents.models import LoreEntry, SwarmMemoryEntry
from mcp_core.models import Tag


def optimize_myth_architecture() -> Dict[str, List[str]]:
    """Analyze lore usage and suggest refactors."""

    deprecated: List[str] = []
    overused: List[str] = []
    conflicting: List[str] = []
    archetype_drift: List[str] = []
    merges: List[str] = []

    entries = LoreEntry.objects.all()
    titles = [e.title for e in entries]

    # Very naive placeholder heuristics
    seen = {}
    for title in titles:
        key = title.split()[0].lower() if title else ""
        seen[key] = seen.get(key, 0) + 1
    overused = [k for k, v in seen.items() if v > 2]

    report = {
        "deprecated_symbols": deprecated,
        "overused_metaphors": overused,
        "conflicting_myth_roots": conflicting,
        "archetype_drift_patterns": archetype_drift,
        "suggested_lore_merges": merges,
    }

    entry = SwarmMemoryEntry.objects.create(
        title="Myth Architecture Optimization", content=json.dumps(report), origin="myth_refactor"
    )
    for name in ["myth_refactor", "lore_collapse", "belief_map"]:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": name})
        entry.tags.add(tag)

    return report
