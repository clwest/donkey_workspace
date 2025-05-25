from rest_framework.routers import DefaultRouter
from django.urls import path
from .views.rewire import (
    SwarmAgentRouteViewSet,
    AgentSymbolicMapViewSet,
    RitualRewiringProposalViewSet,
    swarm_graph,
)

router = DefaultRouter()
router.register(r"rewire", SwarmAgentRouteViewSet, basename="swarm-agent-route")
router.register(r"maps", AgentSymbolicMapViewSet, basename="agent-symbolic-map")
router.register(r"proposals", RitualRewiringProposalViewSet, basename="ritual-rewire-proposal")

urlpatterns = router.urls + [
    path("graph/", swarm_graph, name="swarm-graph"),
]
