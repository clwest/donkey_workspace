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


urlpatterns = router.urls + [
    path("run/", SimulationRunView.as_view(), name="simulation-run"),
    path("roleplay-module/", RoleplayPersonaModuleView.as_view(), name="roleplay-module"),
    path("dreamframe/generate", dreamframe_generate, name="dreamframe-generate"),
    path("scenario/play", scenario_play, name="scenario-play"),
    path("lab/narrative", narrative_lab, name="narrative-lab"),

]
