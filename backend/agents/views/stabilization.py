from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from agents.models.stabilization import (
    BeliefCascadeGraph,
    CascadeImpactNode,
    CascadeEffectTrace,
    RoleTensionMetric,
    AssistantArchetypeConflict,
    CollisionResolutionProposal,
    StabilizationCampaign,
    CodexClauseVoteLog,
    CampaignSymbolicGainEstimate,
)
from agents.serializers import (
    BeliefCascadeGraphSerializer,
    RoleTensionMetricSerializer,
    StabilizationCampaignSerializer,
)


@api_view(["GET"])
def belief_cascade(request, clause_id):
    """Return or create a cascade graph for the given clause."""
    graph, created = BeliefCascadeGraph.objects.get_or_create(clause_id=clause_id)
    return Response(BeliefCascadeGraphSerializer(graph).data)


@api_view(["GET"])
def swarm_collisions(request):
    """List role tension metrics across assistants."""
    tensions = RoleTensionMetric.objects.all().order_by("-created_at")
    return Response(RoleTensionMetricSerializer(tensions, many=True).data)


@api_view(["GET", "POST"])
def stabilization_campaigns(request):
    if request.method == "GET":
        campaigns = StabilizationCampaign.objects.all().order_by("-created_at")
        return Response(StabilizationCampaignSerializer(campaigns, many=True).data)

    serializer = StabilizationCampaignSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    campaign = serializer.save()
    return Response(StabilizationCampaignSerializer(campaign).data, status=status.HTTP_201_CREATED)
