from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response

from assistants.models import Assistant
from metrics.models import RitualPerformanceMetric
from agents.models.lore import DialogueCodexMutationLog, SwarmCodex
from agents.models.federation import SwarmFederationEngine
from agents.models.identity import SymbolicIdentityCard
from simulation.models import MythflowSession


class WorldMetricsView(APIView):
    """Return high-level swarm metrics for the world dashboard."""

    def get(self, request):
        now = timezone.now()
        active_assistants = Assistant.objects.filter(is_active=True).count()
        rituals_per_hour = RitualPerformanceMetric.objects.filter(
            created_at__gte=now - timedelta(hours=1)
        ).count()
        codex_mutation_volume = DialogueCodexMutationLog.objects.filter(
            created_at__gte=now - timedelta(days=1)
        ).count()
        engine = SwarmFederationEngine.objects.order_by("-last_synced").first()
        swarm_entropy = 0.0
        belief_convergence = 0.0
        if engine:
            swarm_entropy = engine.symbolic_state_map.get("entropy", 0.0)
            belief_convergence = engine.ritual_convergence_score
        data = {
            "active_assistants": active_assistants,
            "rituals_per_hour": rituals_per_hour,
            "codex_mutation_volume": codex_mutation_volume,
            "swarm_entropy": swarm_entropy,
            "belief_convergence": belief_convergence,
        }
        return Response(data)


class AssistantPresenceView(APIView):
    """Return assistant presence counts by archetype."""

    def get(self, request):
        data = (
            SymbolicIdentityCard.objects.values("archetype")
            .annotate(count=Count("id"))
            .order_by("archetype")
        )
        return Response(list(data))


class MythflowHeatmapView(APIView):
    """Return heatmap data showing mythflow session counts per codex."""

    def get(self, request):
        data = (
            SwarmCodex.objects.annotate(session_count=Count("mythflowsession"))
            .values("title", "session_count")
            .order_by("title")
        )
        return Response(list(data))
