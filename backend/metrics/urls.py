import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.dashboard import PerformanceDashboardView
from .views import (
    RitualPerformanceMetricListCreateView,
    WorldMetricsView,
    AssistantPresenceView,
    MythflowHeatmapView,
)

urlpatterns = [
    path(
        "performance/<uuid:assistant_id>/",
        PerformanceDashboardView.as_view(),
        name="performance-dashboard",
    ),
    path(
        "ritual-metrics/",
        RitualPerformanceMetricListCreateView.as_view(),
        name="ritual-performance-metric-list",
    ),
    path(
        "world-metrics/",
        WorldMetricsView.as_view(),
        name="world-metrics",
    ),
    path(
        "assistant-presence/",
        AssistantPresenceView.as_view(),
        name="assistant-presence",
    ),
    path(
        "mythflow-heatmap/",
        MythflowHeatmapView.as_view(),
        name="mythflow-heatmap",
    ),
]
