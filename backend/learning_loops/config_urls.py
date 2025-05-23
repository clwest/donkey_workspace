import warnings

warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.config import AdaptiveLoopConfigListCreateView

urlpatterns = [
    path(
        "configs/",
        AdaptiveLoopConfigListCreateView.as_view(),
        name="adaptive-loop-config-list",
    ),
]
