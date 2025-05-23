import warnings

warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.orchestrate import WorkflowOrchestrateView
from .views.api import WorkflowDefinitionListCreateView, WorkflowExecutionLogListView

urlpatterns = [
    path("execute/", WorkflowOrchestrateView.as_view(), name="workflow-execute"),
    path(
        "definitions/",
        WorkflowDefinitionListCreateView.as_view(),
        name="workflow-definition-list",
    ),
    path(
        "logs/",
        WorkflowExecutionLogListView.as_view(),
        name="workflow-execution-log-list",
    ),
]
