from django.utils import timezone

from agents.models import SwarmMemoryEntry, SwarmCodex


def generate_ritual_from_ecosystem_state() -> dict:
    """Propose a ritual based on swarm memory and codex pressure."""

    memory_entropy = SwarmMemoryEntry.objects.count() % 10
    codex_pressure = SwarmCodex.objects.count()
    tension = memory_entropy * (codex_pressure + 1)

    ritual = {
        "name": "Ecosystem Balancing Ritual",
        "tension_score": tension,
        "timestamp": timezone.now().isoformat(),
        "steps": ["gather signals", "align codices", "broadcast symbol"],
    }
    return ritual
