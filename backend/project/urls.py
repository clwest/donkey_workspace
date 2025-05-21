# project/urls.py

from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    ProjectTaskViewSet,
    ProjectMilestoneViewSet,
    assign_role,
    team_memory,
    team_reflections,
)
from django.urls import path
from story.views import ProjectStoriesViewSet

router = DefaultRouter()
router.register(r"", ProjectViewSet, basename="projects")

urlpatterns = router.urls + [
    # Nested routes for project-specific stories
    path(
        "<int:project_pk>/stories/",
        ProjectStoriesViewSet.as_view({"get": "list", "post": "create"}),
        name="project-stories-list",
    ),
    path(
        "<int:project_pk>/stories/<int:pk>/",
        ProjectStoriesViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="project-stories-detail",
    ),
    path("<uuid:id>/assign_role/", assign_role, name="assign-role"),
    path("<uuid:id>/team_memory/", team_memory, name="team-memory"),
    path(
        "<uuid:id>/team_reflections/",
        team_reflections,
        name="team-reflections",
    ),
    path(
        "<uuid:project_pk>/tasks/",
        ProjectTaskViewSet.as_view({"get": "list", "post": "create"}),
        name="project-task-list",
    ),
    path(
        "<uuid:project_pk>/tasks/<uuid:pk>/",
        ProjectTaskViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="project-task-detail",
    ),
    path(
        "<uuid:project_pk>/milestones/",
        ProjectMilestoneViewSet.as_view({"get": "list", "post": "create"}),
        name="project-milestone-list",
    ),
    path(
        "<uuid:project_pk>/milestones/<uuid:pk>/",
        ProjectMilestoneViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="project-milestone-detail",
    ),
]
