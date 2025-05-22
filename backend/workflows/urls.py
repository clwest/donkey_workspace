import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.orchestrate import WorkflowOrchestrateView

urlpatterns = [
    path("execute/", WorkflowOrchestrateView.as_view(), name="workflow-execute"),
]
