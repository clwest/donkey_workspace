from django.urls import path
from . import views

from .views import agents

urlpatterns = [
    path("", agents.list_agents),
    path("<uuid:id>/feedback/", agents.agent_feedback_logs),
    path("<uuid:id>/update-from-feedback/", agents.update_agent_from_feedback),
    path("<slug:slug>/", agents.agent_detail_view),
]