import warnings

warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.trigger import AdaptiveLoopTriggerView
from .views.config import AdaptiveLoopConfigListCreateView
from .views import LearningTrailNodeListCreateView

urlpatterns = [
    path(
        "trigger/<uuid:assistant_id>/",
        AdaptiveLoopTriggerView.as_view(),
        name="adaptive-loop-trigger",
    ),
    path(
        "configs/",
        AdaptiveLoopConfigListCreateView.as_view(),
        name="adaptive-loop-config-list",
    ),
    path(
        "trails/",
        LearningTrailNodeListCreateView.as_view(),
        name="learning-trail-node-list",
    ),
]
