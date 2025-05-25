from rest_framework import viewsets
from ..models.rewire import SwarmAgentRoute, AgentSymbolicMap
from ..serializers import SwarmAgentRouteSerializer, AgentSymbolicMapSerializer


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
