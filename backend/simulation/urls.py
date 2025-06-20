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

from .views.storyline import CinemythStorylineViewSet
from .views.purpose_loop import PurposeLoopCinematicEngineViewSet
from .views.theater import ReflectiveTheaterSessionViewSet
from .views.playback import (
    MythflowPlaybackSessionViewSet,
    SymbolicMilestoneLogViewSet,
    PersonalRitualGuideViewSet,
    SwarmReflectionThreadViewSet,
    SwarmReflectionPlaybackLogViewSet,
    PromptCascadeLogViewSet,
    CascadeNodeLinkViewSet,
    SimulationClusterStatusViewSet,
    SimulationGridNodeViewSet,
    
)
from .views.dreamframe import (
    DreamframeStoryGeneratorViewSet,
    SimScenarioEngineViewSet,
    MultiUserNarrativeLabViewSet,
    dreamframe_generate,
    scenario_play,
    narrative_lab,
)

from .views.sandbox import SimulationRunView
from .views.codex_simulation import CodexSimulationScenarioViewSet
from .views.ritual_drift import RitualDriftObservationViewSet
from .views.mythgraph import MythgraphNodeViewSet

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

router.register(r"cinemyths", CinemythStorylineViewSet, basename="cinemyth")
router.register(r"purpose-loops", PurposeLoopCinematicEngineViewSet, basename="purpose-loop")
router.register(r"theater-sessions", ReflectiveTheaterSessionViewSet, basename="theater-session")
router.register(r"mythflow-playback", MythflowPlaybackSessionViewSet, basename="mythflow-playback")
router.register(r"milestones", SymbolicMilestoneLogViewSet, basename="milestone")
router.register(r"ritual-guide", PersonalRitualGuideViewSet, basename="ritual-guide")
router.register(r"dreamframes", DreamframeStoryGeneratorViewSet, basename="dreamframe-generator")
router.register(r"scenario-engine", SimScenarioEngineViewSet, basename="scenario-engine")
router.register(r"narrative-labs", MultiUserNarrativeLabViewSet, basename="narrative-lab")
router.register(r"swarm-reflection-threads", SwarmReflectionThreadViewSet, basename="swarm-reflection-thread")
router.register(r"swarm-reflection-playback", SwarmReflectionPlaybackLogViewSet, basename="swarm-reflection-playback")
router.register(r"prompt-cascades", PromptCascadeLogViewSet, basename="prompt-cascade")
router.register(r"cascade-nodes", CascadeNodeLinkViewSet, basename="cascade-node")
router.register(r"simulation-grid", SimulationClusterStatusViewSet, basename="simulation-grid")
router.register(r"simulation-grid-nodes", SimulationGridNodeViewSet, basename="simulation-grid-node")
router.register(r"codex/simulate", CodexSimulationScenarioViewSet, basename="codex-simulate")
router.register(r"ritual/drift", RitualDriftObservationViewSet, basename="ritual-drift")
router.register(r"mythgraph", MythgraphNodeViewSet, basename="mythgraph")



urlpatterns = router.urls + [
    path("run/", SimulationRunView.as_view(), name="simulation-run"),
    path("roleplay-module/", RoleplayPersonaModuleView.as_view(), name="roleplay-module"),
    path("dreamframe/generate", dreamframe_generate, name="dreamframe-generate"),
    path("scenario/play", scenario_play, name="scenario-play"),
    path("lab/narrative", narrative_lab, name="narrative-lab"),
    path(
        "mythgraph/<uuid:assistant_id>/",
        MythgraphNodeViewSet.as_view({"get": "by_assistant"}),
        name="mythgraph-assistant",
    ),

]
