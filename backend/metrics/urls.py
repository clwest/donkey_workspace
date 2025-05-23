import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.dashboard import PerformanceDashboardView
from .views import RitualPerformanceMetricListCreateView

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
]
