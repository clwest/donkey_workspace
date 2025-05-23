import warnings

warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from .views.api import WorkflowExecutionLogListView

urlpatterns = [
    path("", WorkflowExecutionLogListView.as_view(), name="execution-log-list"),
]
