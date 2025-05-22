import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.dashboard import PerformanceDashboardView

urlpatterns = [
    path(
        "performance/<uuid:assistant_id>/",
        PerformanceDashboardView.as_view(),
        name="performance-dashboard",
    ),
]
