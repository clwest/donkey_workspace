import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from rest_framework.routers import DefaultRouter
from .views import StoryAudioViewSet, ElevenLabsVoiceViewSet

router = DefaultRouter()
router.register(r"stories", StoryAudioViewSet)
router.register(r"voices", ElevenLabsVoiceViewSet, basename="elevenlabs-voices")

urlpatterns = router.urls
