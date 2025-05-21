from django.db.models import Count
from django.utils.text import slugify

from agents.models import AgentCluster, SwarmMemoryEntry
from mcp_core.models import Tag


def evaluate_swarm_dynamics():
    """Simulate basic swarm game interactions and store results."""
    clusters = AgentCluster.objects.annotate(agent_count=Count("agents"))
    total_clusters = clusters.count()
    collaboration_events = SwarmMemoryEntry.objects.filter(
        tags__name__iexact="collaboration"
    ).count()
    defection_events = SwarmMemoryEntry.objects.filter(
        tags__name__iexact="defection"
    ).count()
    total_events = collaboration_events + defection_events or 1
    collab_rate = collaboration_events / total_events
    diplomacy_score = round(collab_rate * 100, 2)
    outcome = "cooperative" if collab_rate >= 0.5 else "conflicted"

    summary = (
        f"Clusters: {total_clusters}; "
        f"collab {collaboration_events}, defection {defection_events}; "
        f"score {diplomacy_score:.2f}"
    )

    entry = SwarmMemoryEntry.objects.create(
        title="Swarm Game Dynamics",
        content=summary,
        origin="game_sim",
    )
    tags = []
    for name in ["game_state", "strategy_shift", "diplomatic_outcome"]:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
        tags.append(tag)
    entry.tags.set(tags)

    return {
        "diplomacy_score": diplomacy_score,
        "outcome": outcome,
        "collaboration_rate": collab_rate,
        "defection_rate": defection_events / total_events,
    }
