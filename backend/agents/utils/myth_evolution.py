from typing import Dict
from agents.models import SwarmMemoryEntry


def evolve_myth_elements() -> Dict[str, str]:
    """Naive myth evolution placeholder using recent memory."""

    memories = SwarmMemoryEntry.objects.all().order_by("-created_at")[:3]
    entropy = len(memories)
    proposed_mutation = {
        "entropy": entropy,
        "summary": "auto-evolved myth fragment",
    }
    SwarmMemoryEntry.objects.create(
        title="Myth Evolution", content=str(proposed_mutation), origin="myth_evolution"
    )
    return proposed_mutation
