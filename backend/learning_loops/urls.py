import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.trigger import AdaptiveLoopTriggerView

urlpatterns = [
    path(
        "trigger/<uuid:assistant_id>/",
        AdaptiveLoopTriggerView.as_view(),
        name="adaptive-loop-trigger",
    ),
]
