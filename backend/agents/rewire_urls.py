from rest_framework.routers import DefaultRouter
from .views.rewire import SwarmAgentRouteViewSet, AgentSymbolicMapViewSet

router = DefaultRouter()
router.register(r"rewire", SwarmAgentRouteViewSet, basename="swarm-agent-route")
router.register(r"maps", AgentSymbolicMapViewSet, basename="agent-symbolic-map")

urlpatterns = router.urls
