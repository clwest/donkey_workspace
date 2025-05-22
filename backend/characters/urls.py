import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
# characters/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CharacterProfileViewSet,
    CharacterStyleViewSet,
    CharacterReferenceImageViewSet,
    CharactersByProjectView,
    CharacterSimilarityView,
    CharacterTrainView,
    CharacterTrainingStatusView,
    CharacterProfileSimilarityView,
    CharacterImagesView,
    NameGenerationView,
)

router = DefaultRouter()
router.register(r"profiles", CharacterProfileViewSet, basename="characterprofile")
router.register(r"styles", CharacterStyleViewSet)
router.register(r"reference-images", CharacterReferenceImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Character name generation via OpenAI
    path(
        "names/generate/", NameGenerationView.as_view(), name="generate-character-name"
    ),
    # List characters under a specific project
    path(
        "projects/<int:pk>/characters/",
        CharactersByProjectView.as_view(),
        name="project-characters",
    ),
    # Semantic similarity search
    path("similarity/", CharacterSimilarityView.as_view(), name="character-similarity"),
    # Trigger embedding training task for a character
    path(
        "profiles/<int:pk>/train/", CharacterTrainView.as_view(), name="character-train"
    ),
    # Training status endpoint
    path(
        "profiles/<int:pk>/train_status/",
        CharacterTrainingStatusView.as_view(),
        name="character-training-status",
    ),
    # Find similar characters for a given profile
    path(
        "profiles/<int:pk>/similar/",
        CharacterProfileSimilarityView.as_view(),
        name="character-profile-similarity",
    ),
    # List reference images for a given profile
    path(
        "profiles/<int:pk>/images/",
        CharacterImagesView.as_view(),
        name="character-profile-images",
    ),
]
