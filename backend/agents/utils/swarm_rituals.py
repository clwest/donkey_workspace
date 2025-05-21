from datetime import timedelta
from django.utils import timezone

from agents.models import SwarmMemoryEntry
from .swarm_temporal import get_season_marker


def forecast_swarm_rituals() -> list[dict]:
    """Return upcoming ritual suggestions and store forecast memory."""

    now = timezone.now()
    next_window = now + timedelta(days=90)
    upcoming_season = get_season_marker(next_window)

    suggestions = [
        {
            "title": f"{upcoming_season.title()} Cluster Reorg",
            "details": "Prepare to reshuffle agent clusters for upcoming missions.",
        },
        {
            "title": "Assistant Retirement Review",
            "details": "Evaluate aging assistants for potential retirement and legacy archiving.",
        },
        {
            "title": "Resurrection Cycle",
            "details": "Identify legacy agents for potential resurrection this season.",
        },
        {
            "title": "Council Renewal Vote",
            "details": "Schedule vote to refresh the agent council leadership.",
        },
    ]

    entry = SwarmMemoryEntry.objects.create(
        title=f"Ritual Forecast: {upcoming_season.title()} {next_window.year}",
        content="; ".join(s["title"] for s in suggestions),
        origin="ritual_forecast",
    )

    try:
        from mcp_core.models import Tag

        tag, _ = Tag.objects.get_or_create(
            name="ritual_forecast", defaults={"slug": "ritual_forecast"}
        )
        entry.tags.add(tag)
    except Exception:
        pass

    return suggestions
