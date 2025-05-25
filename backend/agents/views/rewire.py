from rest_framework import viewsets
from ..models.rewire import (
    SwarmAgentRoute,
    AgentSymbolicMap,
    RitualRewiringProposal,
)
from ..serializers import (
    SwarmAgentRouteSerializer,
    AgentSymbolicMapSerializer,
    RitualRewiringProposalSerializer,
)


class SwarmAgentRouteViewSet(viewsets.ModelViewSet):
    queryset = SwarmAgentRoute.objects.all().order_by("-created_at")
    serializer_class = SwarmAgentRouteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        assistant = self.request.GET.get("assistant")
        if assistant:
            qs = qs.filter(from_assistant_id=assistant) | qs.filter(to_assistant_id=assistant)
        return qs.distinct()


class AgentSymbolicMapViewSet(viewsets.ModelViewSet):
    queryset = AgentSymbolicMap.objects.all().order_by("-created_at")
    serializer_class = AgentSymbolicMapSerializer


class RitualRewiringProposalViewSet(viewsets.ModelViewSet):
    queryset = RitualRewiringProposal.objects.all().order_by("-created_at")
    serializer_class = RitualRewiringProposalSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def swarm_graph(request):
    latest_map = AgentSymbolicMap.objects.order_by("-created_at").first()
    data = latest_map.map_data if latest_map else {"nodes": [], "edges": []}
    return Response(data)
