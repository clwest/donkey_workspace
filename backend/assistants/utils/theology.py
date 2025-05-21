from __future__ import annotations

from typing import Dict

from agents.models import (
    AssistantCivilization,
    SwarmMemoryEntry,
    TranscendentMyth,
)


def synthesize_theology_from_memory(civilization: AssistantCivilization) -> Dict:
    """Build a theology from assistant memories."""

    memories = (
        SwarmMemoryEntry.objects.filter(linked_agents__in=civilization.members.all())
        .order_by("-created_at")[:10]
    )
    core_tenets = [m.title for m in memories]

    myth = TranscendentMyth.objects.create(
        title=f"{civilization.name} Unified Belief",
        core_tenets=core_tenets,
        mythic_axis="rebirth",
    )
    myth.sustaining_civilizations.add(civilization)

    return {"myth_id": myth.id, "core_tenets": core_tenets}
