import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path, include

try:
    from sandbox import debugger
except Exception:  # noqa: BLE001
    debugger = None

# images/urls.py
from rest_framework.routers import DefaultRouter
from images.views import (
    ImageViewSet,
    UserImageView,
    PublicImageViewSet,
    EditImageViewSet,
    StyleViewSet,
    UpscaleImageView,
    TagImageViewSet,
    ProjectImageViewSet,
    StableDiffusionGenerationView,
    CheckImageStatusView,
    PromptHelperViewSet,
    ProjectImageGalleryView,
    ThemeHelperViewSet,
    ThemeFavoriteViewSet,
)
from images.views import NarrateSceneView
from images.views import PromptHelperSimilarityView

router = DefaultRouter()
router.register(r"gallery", PublicImageViewSet, basename="public-images")
router.register(r"user-images", UserImageView, basename="user-images")
router.register(r"images", ImageViewSet, basename="images")
router.register(r"edit", EditImageViewSet, basename="edit")
router.register(r"upscale", UpscaleImageView, basename="upscale")
router.register(r"styles", StyleViewSet, basename="styles")
router.register(r"tags", TagImageViewSet, basename="tags")
router.register(r"image-projects", ProjectImageViewSet, basename="image-projects")
router.register(r"prompt-helpers", PromptHelperViewSet, basename="prompt-helpers")
router.register(r"theme-helpers", ThemeHelperViewSet, basename="themehelper")
router.register(r"theme-favorites", ThemeFavoriteViewSet, basename="themefavorite")

# Custom views that aren't model-based
custom_views = [
    path(
        "generate/",
        StableDiffusionGenerationView.as_view({"post": "create"}),
        name="sd-generate",
    ),
    path(
        "status/<int:pk>/",
        CheckImageStatusView.as_view({"get": "retrieve"}),
        name="sd-status",
    ),
]

urlpatterns = []
if debugger:
    urlpatterns.append(
        path("debug/prompts/", debugger.debug_prompts, name="debug-prompts")
    )
urlpatterns += router.urls + custom_views
# Project gallery endpoint
urlpatterns += [
    path(
        "projects/<int:project_id>/gallery/",
        ProjectImageGalleryView.as_view(),
        name="project-gallery",
    ),
]
urlpatterns += [
    # TTS narration for scene images
    path("images/<int:pk>/narrate/", NarrateSceneView.as_view(), name="image-narrate"),
]
urlpatterns += [
    # Semantic similarity for PromptHelpers
    path(
        "prompt-helpers/similar/",
        PromptHelperSimilarityView.as_view(),
        name="prompt-helper-similarity",
    ),
]
