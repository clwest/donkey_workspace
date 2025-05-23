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
from .views.dialogue import SymbolicDialogueScriptViewSet
from .views.decision import MemoryDecisionTreeNodeViewSet
from .views.scene import SceneControlEngineViewSet
from .views.sandbox import SimulationRunView

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
router.register(r"dialogue-scripts", SymbolicDialogueScriptViewSet, basename="dialogue-script")
router.register(r"decision-trees", MemoryDecisionTreeNodeViewSet, basename="decision-tree")
router.register(r"scene-control", SceneControlEngineViewSet, basename="scene-control")

urlpatterns = router.urls + [
    path("run/", SimulationRunView.as_view(), name="simulation-run"),
    path("roleplay-module/", RoleplayPersonaModuleView.as_view(), name="roleplay-module"),
]
