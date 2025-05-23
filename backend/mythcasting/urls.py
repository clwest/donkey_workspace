from rest_framework.routers import DefaultRouter
from .views import (
    CinemythStorylineViewSet,
    MythcastingChannelViewSet,
    AudienceFeedbackLoopViewSet,
    ParticipatoryStreamEventViewSet,
)

router = DefaultRouter()
router.register("storylines", CinemythStorylineViewSet, basename="cinemyth-storyline")
router.register("channels", MythcastingChannelViewSet, basename="mythcasting-channel")
router.register("feedback-loops", AudienceFeedbackLoopViewSet, basename="audience-feedback-loop")
router.register("participatory-streams", ParticipatoryStreamEventViewSet, basename="participatory-stream-event")

urlpatterns = router.urls
