import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from rest_framework.routers import DefaultRouter
from .views import NarrativeEventViewSet

router = DefaultRouter()
router.register(r'', NarrativeEventViewSet, basename='narrative-event')

urlpatterns = router.urls
