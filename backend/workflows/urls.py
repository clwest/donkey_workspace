from django.urls import path
from .views.orchestrate import WorkflowOrchestrateView

urlpatterns = [
    path("execute/", WorkflowOrchestrateView.as_view(), name="workflow-execute"),
]
