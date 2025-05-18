# project/urls.py

from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet
from django.urls import path
from story.views import ProjectStoriesViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")

urlpatterns = router.urls + [
    # Nested routes for project-specific stories
    path(
        "projects/<int:project_pk>/stories/",
        ProjectStoriesViewSet.as_view({"get": "list", "post": "create"}),
        name="project-stories-list",
    ),
    path(
        "projects/<int:project_pk>/stories/<int:pk>/",
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
]
