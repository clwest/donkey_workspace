from datetime import datetime
from django.utils import timezone
from agents.models import Agent, AgentCluster, SwarmMemoryEntry


def get_season_marker(date: datetime) -> str:
    month = date.month
    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    if month in [9, 10, 11]:
        return "fall"
    return "winter"


def get_swarm_snapshot(date: datetime):
    """Return agents, clusters and memories active at the given date."""
    if timezone.is_naive(date):
        date = timezone.make_aware(date)
    return {
        "agents": Agent.objects.filter(created_at__lte=date),
        "clusters": AgentCluster.objects.filter(created_at__lte=date),
        "memories": SwarmMemoryEntry.objects.filter(created_at__lte=date),
    }
