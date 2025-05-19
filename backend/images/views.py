from django.shortcuts import render

# Create your views here.
from dotenv import load_dotenv
from rest_framework import status
import os
from django.conf import settings
from rest_framework.decorators import action
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from django.forms.models import model_to_dict

from .models import (
    Image,
    Edit,
    UpscaleImage,
    ProjectImage,
    PromptHelper,
    PromptHelperVersion,
    SourceImage,
    TagImage,
    ProjectImage,
    ThemeHelper,
    ThemeFavorite,
)
from .serializers import (
    ImageSerializer,
    EditImageSerializer,
    UpscaleImageSerializer,
    PromptHelperSerializer,
    PromptHelperVersionSerializer,
    CarouselImageSerializer,
    SourceImageSerializer,
    TagImageSerializer,
    ProjectImageSerializer,
    ImageDetailSerializer,
    ThemeHelperSerializer,
    ThemeFavoriteSerializer,
)
from .tasks import (
    process_sd_image_request,
    process_edit_image_request,
    process_upscale_image_request,
)
from django.shortcuts import get_object_or_404
from tts.models import SceneAudio
from tts.serializers import SceneAudioSerializer
from tts.tasks import queue_tts_scene
from rest_framework import generics
from images.helpers.permissions import AllowAny
from images.helpers.image_urls import generate_absolute_urls
from images.helpers.prompt_generation_hook import prepare_final_prompt


from urllib.parse import unquote
from rest_framework.views import APIView
from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.vector_utils import compute_similarity

load_dotenv()

logger = logging.getLogger("django")


class PromptHelperSimilarityView(APIView):
    """Retrieve top similar PromptHelpers based on semantic similarity to query."""

    permission_classes = [AllowAny]

    def get(self, request):
        # Decode URL-encoded query parameter
        raw_q = request.query_params.get("query", "")
        query = unquote(raw_q).strip()
        if not query:
            return Response([], status=status.HTTP_200_OK)
        try:
            q_emb = generate_embedding(query)
            if not q_emb:
                return Response([], status=status.HTTP_200_OK)
            results = []
            for helper in PromptHelper.objects.all():
                try:
                    h_emb = generate_embedding(helper.prompt)
                    score = compute_similarity(q_emb, h_emb)
                    results.append(
                        {
                            "id": helper.id,
                            "name": helper.name,
                            "prompt": helper.prompt,
                            "negative_prompt": helper.negative_prompt or "",
                            "score": score,
                        }
                    )
                except Exception:
                    continue
            results.sort(key=lambda x: x["score"], reverse=True)
            return Response(results[:3], status=status.HTTP_200_OK)
        except Exception:
            return Response([], status=status.HTTP_200_OK)


class UserImagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"


class StableDiffusionGenerationView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def _resolve_style(self, style_input):
        if not style_input:
            return None
        if isinstance(style_input, dict):
            lookup = style_input.get("id") or style_input.get("name")
        else:
            lookup = style_input
        if str(lookup).isdigit():
            return PromptHelper.objects.filter(id=int(lookup)).first()
        return PromptHelper.objects.filter(name__iexact=str(lookup)).first()

    def create(self, request):
        logger.info("🎨 Received SD generation request.")
        user = request.user
        data = request.data

        try:
            prompt = data.get("prompt", "").strip()
            negative_prompt = data.get("negative_prompt", "").strip()
            width = int(data.get("width", 1024))
            height = int(data.get("height", 1024))
            steps = int(data.get("steps", 50))
            style_input = data.get("style")

            if not prompt:
                return Response(
                    {"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            style_instance = self._resolve_style(style_input)

            if style_instance:
                logger.info(f"🎨 Style matched: {style_instance.name}")
            else:
                logger.info("🎨 No style matched, proceeding with raw prompt.")

            # Create image request with default order (non-negative)
            image_request = Image.objects.create(
                user=user,
                prompt=prompt,
                description=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                order=0,
                steps=steps,
                style=style_instance,
                engine_used="stable-diffusion",
                status="queued",
            )

            # 🔁 Let Celery handle prompt prep via hook
            process_sd_image_request.delay(image_request.id)

            # Serialize response using PromptHelperSerializer for style to avoid raw FileFields
            style_data = (
                PromptHelperSerializer(style_instance).data if style_instance else None
            )
            return Response(
                {
                    "message": "Image generation request queued.",
                    "request_id": image_request.id,
                    "status": image_request.status,
                    "style": style_data,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as ve:
            logger.error(f"⚠️ ValueError: {ve}")
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("🔥 Unexpected error in StableDiffusionGenerationView")
            return Response(
                {"error": "Internal error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CheckImageStatusView(viewsets.ViewSet):
    authentication_classes = []  # 👈 No auth
    permission_classes = [AllowAny]  # 👈 Public access

    def retrieve(self, request, pk=None):
        try:
            image_request = Image.objects.get(id=pk)
            return Response(
                {
                    "status": image_request.status,
                    "output_urls": image_request.output_urls,
                }
            )
        except Image.DoesNotExist:
            return Response(
                {"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ImageViewSet(ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, JSONParser, FormParser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ImageDetailSerializer
        return ImageSerializer


class UserImageView(viewsets.ModelViewSet):
    """
    Handles authenticated user image access with support for search and filtering.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = ImageSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    pagination_class = UserImagePagination
    search_fields = ["title", "description", "prompt"]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["delete"], url_path="delete-broken")
    def delete_broken_images(self, request):
        """
        Deletes all images for the current user that have no output_url or output_urls.
        """
        broken_images = self.get_queryset().filter(
            output_url__isnull=True, output_urls__isnull=True
        )

        count = broken_images.count()

        for img in broken_images:
            if img.file_path:
                file_path = os.path.join(settings.MEDIA_ROOT, img.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            img.delete()

        return Response(
            {"message": f"🗑️ Deleted {count} broken image(s)."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="retry")
    def retry_failed(self, request, pk=None):
        """
        Re-queue a failed image generation request.
        """
        try:
            image = self.get_queryset().get(id=pk)

            if image.status != "failed":
                return Response(
                    {"error": "Only failed requests can be retried."}, status=400
                )

            # Reset status and re-queue
            image.status = "queued"
            image.output_url = None
            image.output_urls = []
            image.file_path = None
            image.save()

            process_sd_image_request.delay(image.id)

            return Response(
                {
                    "message": f"🌀 Image {image.id} re-queued for generation.",
                    "status": "queued",
                },
                status=202,
            )

        except Image.DoesNotExist:
            return Response({"error": "Image not found."}, status=404)


class PublicImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [AllowAny]  # optional: make it AllowAny later

    def get_queryset(self):
        return self.queryset.filter(is_public=True).order_by("-created_at")

    @action(detail=False, methods=["get"], url_path="carousel")
    def carousel(self, request):
        project = (
            ProjectImage.objects.filter(is_featured=True)
            .order_by("-created_at")
            .first()
        )
        if not project:
            return Response([])

        images = (
            Image.objects.filter(
                project=project, is_public=True, output_url__isnull=False
            )
            .exclude(output_url="")
            .order_by("?")[:10]
        )
        serializer = CarouselImageSerializer(images, many=True)
        return Response(serializer.data)


class UpscaleImageView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def list(self, request):
        # Return all upscaled images by the current user
        upscaled_images = UpscaleImage.objects.filter(user=request.user).order_by(
            "-created_at"
        )
        serializer = UpscaleImageSerializer(upscaled_images, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            upscaled = UpscaleImage.objects.get(id=pk, user=request.user)
            serializer = UpscaleImageSerializer(upscaled)
            return Response(serializer.data)
        except UpscaleImage.DoesNotExist:
            return Response({"error": "Upscaled image not found."}, status=404)

    def create(self, request):
        try:
            request_id = request.data.get("request_id")
            upscale_type = request.data.get("upscale_type", "conservative").lower()
            scale = request.data.get("scale", 0.35)
            prompt = request.data.get("prompt", "Highly detailed upscale")

            if upscale_type not in ["conservative", "creative", "fast"]:
                return Response({"error": "Invalid upscale type."}, status=400)

            if not request_id:
                return Response({"error": "Missing request_id"}, status=400)

            try:
                image = Image.objects.get(id=request_id, user=request.user)
            except Image.DoesNotExist:
                return Response({"error": "Image request not found."}, status=404)

            payload = {
                "request_id": image.id,
                "user_id": request.user.id,
                "upscale_type": upscale_type,
                "scale": scale,
                "prompt": prompt,
            }

            process_upscale_image_request.delay(payload)

            return Response(
                {
                    "message": f"{upscale_type.capitalize()} upscaling started",
                    "request_id": image.id,
                },
                status=202,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class EditImageViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def create(self, request):
        try:
            image_id = request.data.get("image_id")
            edit_type = request.data.get("edit_type")
            prompt = request.data.get("prompt")
            seed = request.data.get("seed")
            style_preset = request.data.get("style_preset")

            if not image_id or not edit_type:
                return Response({"error": "Missing required fields."}, status=400)

            image = Image.objects.get(id=image_id, user=request.user)

            edit = Edit.objects.create(
                request=image,
                user=request.user,
                edit_type=edit_type,
                prompt=prompt,
                seed=seed,
                style_preset=style_preset,
            )

            payload = {
                "edit_id": edit.id,
                "user_id": request.user.id,
            }
            process_edit_image_request.delay(payload)

            return Response(
                {
                    "message": f"{edit_type.capitalize()} edit started",
                    "edit_id": edit.id,
                },
                status=202,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class StyleViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = PromptHelper.objects.all()
    serializer_class = PromptHelperSerializer
    permission_classes = [AllowAny]


class TagImageViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = TagImage.objects.all()
    serializer_class = TagImageSerializer


class ProjectImageViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = ProjectImage.objects.filter(is_published=True)
    serializer_class = ProjectImageSerializer


class PromptHelperViewSet(viewsets.ModelViewSet):
    queryset = PromptHelper.objects.all()
    serializer_class = PromptHelperSerializer
    # Disable pagination to return all prompt helpers in one response
    pagination_class = None
    permission_classes = [AllowAny]
    lookup_field = "id"

    # Nested endpoint: list and create versions
    @action(detail=True, methods=["get", "post"], url_path="versions")
    def versions(self, request, pk=None):
        helper = self.get_object()
        if request.method == "GET":
            vers = helper.versions.all()
            serializer = PromptHelperVersionSerializer(vers, many=True)
            return Response(serializer.data)
        # create new version
        serializer = PromptHelperVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        next_num = helper.versions.count() + 1
        version = PromptHelperVersion.objects.create(
            helper=helper,
            version_number=next_num,
            prompt=serializer.validated_data["prompt"],
            negative_prompt=serializer.validated_data.get("negative_prompt", ""),
            notes=serializer.validated_data.get("notes", ""),
        )
        # set as current version
        helper.current_version = version
        helper.save(update_fields=["current_version"])
        out_ser = PromptHelperVersionSerializer(version)
        return Response(out_ser.data, status=status.HTTP_201_CREATED)

    # Preview a specific version without changing current_version
    @action(
        detail=True, methods=["get"], url_path="preview-version/(?P<version_id>[^/.]+)"
    )
    def preview_version(self, request, pk=None, version_id=None):
        helper = self.get_object()
        try:
            ver = helper.versions.get(pk=version_id)
        except PromptHelperVersion.DoesNotExist:
            return Response(
                {"detail": "Version not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {
                "prompt": ver.prompt,
                "negative_prompt": ver.negative_prompt,
            }
        )

    # Rollback to a specific version
    @action(
        detail=True,
        methods=["post"],
        url_path="rollback-version/(?P<version_id>[^/.]+)",
    )
    def rollback_version(self, request, pk=None, version_id=None):
        helper = self.get_object()
        try:
            ver = helper.versions.get(pk=version_id)
        except PromptHelperVersion.DoesNotExist:
            return Response(
                {"detail": "Version not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # perform rollback
        helper.current_version = ver
        # update legacy fields if desired
        helper.prompt = ver.prompt
        helper.negative_prompt = ver.negative_prompt
        helper.save(update_fields=["current_version", "prompt", "negative_prompt"])
        # return updated helper
        helper_ser = PromptHelperSerializer(helper)
        return Response(helper_ser.data)


class ProjectImageGalleryView(generics.ListAPIView):
    """
    List all images associated with a given project.
    """

    serializer_class = ImageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        return Image.objects.filter(project_id=project_id).order_by("created_at")


class NarrateSceneView(APIView):
    """API view to handle TTS narration for a scene image."""

    permission_classes = [AllowAny]

    def post(self, request, pk=None):
        # Start narration for the given image
        image = get_object_or_404(Image, id=pk)
        # Use the image prompt for narration
        narration_prompt = image.prompt
        # Optional voice and provider
        voice = request.data.get("voice_style")
        provider = request.data.get("provider")
        # Create SceneAudio entry
        scene_audio = SceneAudio.objects.create(
            user=request.user,
            image=image,
            prompt=narration_prompt,
            voice_style=voice,
            provider=provider,
            status="queued",
        )
        # Enqueue async TTS task
        task = queue_tts_scene.delay(scene_audio.id)
        scene_audio.task_id = task.id
        scene_audio.save(update_fields=["task_id"])
        # Return initial serializer data
        serializer = SceneAudioSerializer(scene_audio, context={"request": request})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def get(self, request, pk=None):
        # Get latest narration status for the image
        scene_audio = (
            SceneAudio.objects.filter(image_id=pk).order_by("-created_at").first()
        )
        if not scene_audio:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SceneAudioSerializer(scene_audio, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ThemeHelperViewSet(viewsets.ModelViewSet):
    """
    CRUD for ThemeHelper.
    GET returns public themes or themes created by the requesting user.
    """

    serializer_class = ThemeHelperSerializer
    permission_classes = [AllowAny]
    # Support JSON and multipart (for preview_image uploads)
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "category",
        "is_featured",
        "is_builtin",
        "is_public",
        "created_by",
    ]
    search_fields = ["name", "description", "tags"]

    def get_queryset(self):
        user = self.request.user
        base_qs = ThemeHelper.objects.all()
        if user and user.is_authenticated:
            return base_qs.filter((Q(is_public=True)) | Q(created_by=user)).order_by(
                "name"
            )
        return base_qs.filter(is_public=True).order_by("name")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def remix(self, request, pk=None):
        """
        Create a duplicate (remix) of the specified theme, mark it as user-owned and private,
        and return the new theme instance.
        """
        # Get the original theme
        original = self.get_object()
        # Duplicate core fields
        # JSONField 'tags' will copy list; M2M recommended_styles handled below
        new_theme = ThemeHelper.objects.create(
            name=original.name,
            description=original.description,
            prompt=original.prompt,
            negative_prompt=original.negative_prompt,
            category=original.category,
            tags=list(original.tags) if hasattr(original, "tags") else [],
            is_builtin=False,
            is_public=False,
            is_fork=True,
            parent=original,
            created_by=request.user,
        )
        # Copy many-to-many recommended styles
        try:
            new_theme.recommended_styles.set(original.recommended_styles.all())
        except Exception:
            pass
        # Serialize and return the new theme
        serializer = self.get_serializer(new_theme)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ViewSet for user theme favorites
class ThemeFavoriteViewSet(viewsets.ModelViewSet):
    """CRUD for user favorites of themes. Users can favorite/unfavorite themes."""

    serializer_class = ThemeFavoriteSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme"]
    lookup_field = "theme"

    def get_queryset(self):
        # Only favorites belonging to the requesting user
        return ThemeFavorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Associate favorite with requesting user
        serializer.save(user=self.request.user)
