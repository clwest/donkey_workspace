import warnings

warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views.config import SimulationConfigViewSet
from .views.simulator import MythScenarioSimulatorViewSet
from .views.state import SimulationStateTrackerViewSet
from .views.ritual import RitualInteractionEventViewSet
from .views.session import (
    MythflowSessionViewSet,
    SymbolicDialogueExchangeViewSet,
    RoleplayPersonaModuleView,
)
from .views.sandbox import SimulationRunView
from .views.projection import (
    memory_projection_frames,
    belief_walkthroughs,
    dreamframes,
)

router = DefaultRouter()
router.register(r"simulators", MythScenarioSimulatorViewSet, basename="myth-simulator")
router.register(
    r"simulation-state", SimulationStateTrackerViewSet, basename="simulation-state"
)
router.register(
    r"ritual-launcher", RitualInteractionEventViewSet, basename="ritual-launcher"
)
router.register(r"config", SimulationConfigViewSet, basename="simulation-config")
router.register(r"mythflow-sessions", MythflowSessionViewSet, basename="mythflow-session")
router.register(r"dialogue-exchange", SymbolicDialogueExchangeViewSet, basename="dialogue-exchange")

urlpatterns = router.urls + [
    path("run/", SimulationRunView.as_view(), name="simulation-run"),
    path("roleplay-module/", RoleplayPersonaModuleView.as_view(), name="roleplay-module"),
    path("memory-projection/", memory_projection_frames, name="memory-projection"),
    path("belief-walkthroughs/", belief_walkthroughs, name="belief-walkthroughs"),
    path("dreamframes/", dreamframes, name="dreamframes"),
]
