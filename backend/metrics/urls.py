import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.dashboard import PerformanceDashboardView
from .views import (
    RitualPerformanceMetricListCreateView,
    WorldMetricsView,
    AssistantPresenceView,
    MythflowHeatmapView,
    RitualReputationScoreListView,
    CodexClauseVoteListView,
    SwarmAlignmentIndexView,
    SwarmTaskEvolutionView,
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
    path(
        "ritual/reputation/",
        RitualReputationScoreListView.as_view(),
        name="ritual-reputation",
    ),
    path(
        "codex/vote/",
        CodexClauseVoteListView.as_view(),
        name="codex-clause-vote",
    ),
    path(
        "swarm/alignment/",
        SwarmAlignmentIndexView.as_view(),
        name="swarm-alignment-index",
    ),
    path(
        "evolve/swarm/",
        SwarmTaskEvolutionView.as_view(),
        name="swarm-task-evolution",
    ),
]
