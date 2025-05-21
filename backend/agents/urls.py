from django.urls import path
from . import views

from .views import agents

urlpatterns = [
    path("swarm-temporal-report/", agents.swarm_temporal_report),
    path("swarm-memory/", agents.swarm_memory),
    path("swarm-snapshot/<str:date>/", agents.swarm_snapshot_view),
    path("retire/", agents.retire_agents),
    path("clusters/", agents.list_clusters),
    path("clusters/<uuid:id>/", agents.cluster_detail_view),
    path("", agents.list_agents),
    path("<uuid:id>/feedback/", agents.agent_feedback_logs),
    path("<uuid:id>/update-from-feedback/", agents.update_agent_from_feedback),
    path("<uuid:id>/train/", agents.train_agent),
    path("<uuid:id>/recommend-training-docs/", agents.recommend_training_docs),
    path("<slug:slug>/", agents.agent_detail_view),
]