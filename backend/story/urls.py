import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from rest_framework.routers import DefaultRouter
from .views import StoryViewSet, storyboard_list

router = DefaultRouter()
router.register(r"", StoryViewSet, basename="stories")

urlpatterns = router.urls
from .views import StoryViewSet
from django.urls import path

# Additional actions on StoryViewSet
urlpatterns += [
    path(
        "<int:pk>/tag-chunks/",
        StoryViewSet.as_view({"post": "tag_chunks"}),
        name="story-tag-chunks",
    ),
    path(
        "<int:pk>/chunk-tags/",
        StoryViewSet.as_view({"get": "chunk_tags"}),
        name="story-chunk-tags",
    ),
    # Aggregate top tags from story chunks
    path("<int:pk>/tags/", StoryViewSet.as_view({"get": "tags"}), name="story-tags"),
    path("events/", storyboard_list, name="storyboard-list"),
]
