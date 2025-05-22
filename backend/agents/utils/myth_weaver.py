from __future__ import annotations

from typing import List, Dict
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry


def weave_recursive_myth(assistant: Assistant, depth: int = 3) -> Dict[str, List[Dict[str, str]]]:
    """Construct a simple recursive myth narrative from recent memories."""
    memories = list(SwarmMemoryEntry.objects.all().order_by("-created_at")[:depth])
    fragments = []
    reflection = ""
    for idx, mem in enumerate(memories):
        prophecy = f"prophecy-{idx}"
        fragment = {
            "memory": mem.content,
            "prophecy": prophecy,
            "reflection": reflection,
        }
        fragments.append(fragment)
        reflection = f"{reflection} {prophecy}".strip()

    summary = SwarmMemoryEntry.objects.create(
        title=f"Myth weaving for {assistant.name}",
        content=str(fragments),
        origin="myth_weaver",
    )
    return {"assistant": assistant.id, "fragments": fragments, "summary_entry": summary.id}
