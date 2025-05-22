import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
# project/urls.py

from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    ProjectTaskViewSet,
    ProjectMilestoneViewSet,
)
from django.urls import path, include
from story.views import ProjectStoriesViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")

api_urlpatterns = [
    path("api/v1/", include(router.urls)),
    path(
        "api/v1/projects/<uuid:project_pk>/stories/",
        ProjectStoriesViewSet.as_view({"get": "list", "post": "create"}),
        name="project-stories-list",
    ),
    path(
        "api/v1/projects/<uuid:project_pk>/stories/<uuid:pk>/",
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
    path(
        "api/v1/projects/<uuid:project_pk>/tasks/",
        ProjectTaskViewSet.as_view({"get": "list", "post": "create"}),
        name="project-task-list",
    ),
    path(
        "api/v1/projects/<uuid:project_pk>/tasks/<uuid:pk>/",
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
        "api/v1/projects/<uuid:project_pk>/milestones/",
        ProjectMilestoneViewSet.as_view({"get": "list", "post": "create"}),
        name="project-milestone-list",
    ),
    path(
        "api/v1/projects/<uuid:project_pk>/milestones/<uuid:pk>/",
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

# Deprecated unversioned routes
deprecated_urlpatterns = router.urls + [
    path(
        "<uuid:project_pk>/stories/",
        ProjectStoriesViewSet.as_view({"get": "list", "post": "create"}),
        name="project-stories-list-deprecated",
    ),
    path(
        "<uuid:project_pk>/stories/<uuid:pk>/",
        ProjectStoriesViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="project-stories-detail-deprecated",
    ),
    path(
        "<uuid:project_pk>/tasks/",
        ProjectTaskViewSet.as_view({"get": "list", "post": "create"}),
        name="project-task-list-deprecated",
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
        name="project-task-detail-deprecated",
    ),
    path(
        "<uuid:project_pk>/milestones/",
        ProjectMilestoneViewSet.as_view({"get": "list", "post": "create"}),
        name="project-milestone-list-deprecated",
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
        name="project-milestone-detail-deprecated",
    ),
]

urlpatterns = api_urlpatterns + deprecated_urlpatterns
