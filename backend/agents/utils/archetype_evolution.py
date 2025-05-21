import json
from agents.models import MissionArchetype, SwarmMemoryEntry
from assistants.models import AssistantReflectionLog


def evolve_archetype_profile(archetype: MissionArchetype) -> dict:
    """Analyze reflections to mutate archetype traits and log the result."""
    reflections = AssistantReflectionLog.objects.order_by("-created_at")[:5]
    descriptor = {
        "name": archetype.name,
        "description": archetype.description,
        "core_skills": archetype.core_skills,
        "preferred_cluster_structure": archetype.preferred_cluster_structure,
        "insights": [r.summary for r in reflections],
    }
    SwarmMemoryEntry.objects.create(
        title=f"Archetype shift for {archetype.name}",
        content=json.dumps(descriptor, indent=2),
        origin="archetype_shift",
    )
    return descriptor
