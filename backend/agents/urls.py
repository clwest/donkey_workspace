from django.urls import path
from . import views

from .views import agents

urlpatterns = [
    path("", agents.list_agents),
    path("<slug:slug>/", agents.agent_detail_view),
]