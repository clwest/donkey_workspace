from rest_framework import serializers
from .models import (
    Image,
    UpscaleImage,
    Edit,
    PromptHelper,
    PromptHelperVersion,
    TagImage,
    ProjectImage,
    SourceImage,
    ThemeHelper,
    ThemeFavorite,
)

from characters.models import CharacterProfile


class ImageSerializer(serializers.ModelSerializer):
    style = serializers.SerializerMethodField()
    style_id = serializers.PrimaryKeyRelatedField(
        queryset=PromptHelper.objects.all(),
        source="style",
        write_only=True,
        required=False,
    )
    output_urls = serializers.SerializerMethodField()
    # Associated story and project titles for context
    story_title = serializers.ReadOnlyField(source="story.title")
    project_title = serializers.ReadOnlyField(source="project.title")
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    model_used = serializers.CharField(required=False, allow_blank=True)
    engine_used = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField()
    # Generation backend: stability (SDXL), replicate, or openai
    model_backend = serializers.ChoiceField(
        choices=Image.MODEL_BACKEND_CHOICES,
        default=Image.MODEL_BACKEND_CHOICES[0][0],
        help_text="Generation backend to use",
    )
    # External job ID for replicate/OpenAI
    prediction_id = serializers.CharField(read_only=True)
    # Represent the owning user by their string (username)
    user = serializers.StringRelatedField(read_only=True)
    character = serializers.PrimaryKeyRelatedField(
        queryset=CharacterProfile.objects.all(), required=False
    )
    caption = serializers.CharField(
        source="description", allow_blank=True, required=False
    )
    alt_text = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Image
        # Include all model fields plus custom fields
        fields = "__all__"

    def get_url(self, obj):
        if obj.output_urls:
            return obj.output_urls[0]
        return None

    def get_style(self, obj):
        if not obj.style:
            return None
        return {
            "id": obj.style.id,
            "name": obj.style.name,
            "prompt": obj.style.prompt,
            "negative_prompt": obj.style.negative_prompt,
            "image_url": self.get_image_url(obj.style),
            "is_builtin": obj.style.is_builtin,
        }

    def get_image_url(self, style):
        try:
            if style.image_path and hasattr(style.image_path, "url"):
                return style.image_path.url
        except Exception:
            return None
        return None

    def get_output_urls(self, obj):
        return obj.output_urls if obj.output_urls else []

    def get_engine_used(self, obj):
        if obj.engine_used == "dalle":
            return "DALL·E"
        elif obj.engine_used == "stable-diffusion":
            return "Stable Diffusion"
        return obj.engine_used  # fallback raw string


class ImageDetailSerializer(ImageSerializer):
    upscaled_versions = serializers.SerializerMethodField()

    class Meta(ImageSerializer.Meta):
        # Include all model fields and declared method fields (including upscaled_versions)
        fields = "__all__"

    def get_upscaled_versions(self, obj):
        upscales = obj.upscale_images.all().order_by("-created_at")
        return UpscaleImageSerializer(upscales, many=True).data


class UpscaleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpscaleImage
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at"]


class EditImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edit
        fields = [
            "id",
            "request",
            "file_path",
            "output_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PromptHelperSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    # Include current version metadata
    current_version = serializers.SerializerMethodField()

    class Meta:
        model = PromptHelper
        fields = [
            "id",
            "name",
            "prompt",
            "negative_prompt",
            "image_url",
            "is_builtin",
            "voice_style",
            "current_version",
        ]

    def get_image_url(self, obj):
        try:
            if obj.image_path and hasattr(obj.image_path, "url"):
                return obj.image_path.url
        except (ValueError, Exception):
            return None
        return None

    def get_current_version(self, obj):
        ver = obj.current_version
        if not ver:
            return None
        # return minimal info
        return {
            "id": ver.id,
            "version_number": ver.version_number,
            "created_at": ver.created_at.isoformat(),
        }


class TagImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagImage
        fields = "__all__"


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = "__all__"


class SourceImageSerializer(serializers.ModelSerializer):
    tags = TagImageSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        required=False,
        source="tags",
        queryset=TagImage.objects.all(),
    )
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SourceImage
        fields = [
            "id",
            "image_file",
            "title",
            "description",
            "purpose",
            "tags",
            "tag_ids",
            "is_public",
            "user",
            "uploaded_at",
        ]
        read_only_fields = ["id", "user", "uploaded_at"]


class CarouselImageSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    project_slug = serializers.CharField(source="project.slug", read_only=True)
    title = serializers.CharField(read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = [
            "id",
            "output_url",
            "prompt",
            "title",
            "project",
            "project_name",
            "project_slug",
            "tags",
        ]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


class PromptHelperVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptHelperVersion
        fields = [
            "id",
            "helper",
            "version_number",
            "prompt",
            "negative_prompt",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "helper", "version_number", "created_at"]


# Serializer for user favorites of themes
class ThemeFavoriteSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source="user.id")
    theme_id = serializers.PrimaryKeyRelatedField(
        source="theme", queryset=ThemeHelper.objects.all()
    )

    class Meta:
        model = ThemeFavorite
        fields = ["id", "user_id", "theme_id", "created_at"]
        read_only_fields = ["id", "user_id", "created_at"]


class ThemeHelperSerializer(serializers.ModelSerializer):
    # Read-only username of creator
    created_by_username = serializers.ReadOnlyField(source="created_by.username")
    # Writeable tags list
    tags = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )
    recommended_styles = PromptHelperSerializer(many=True, read_only=True)
    recommended_style_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=PromptHelper.objects.all(),
        source="recommended_styles",
        write_only=True,
        required=False,
    )

    # Include URL for preview image if available
    preview_image_url = serializers.SerializerMethodField()
    # Favorite metadata
    is_favorited = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = ThemeHelper
        fields = [
            "id",
            "name",
            "description",
            "prompt",
            "negative_prompt",
            "category",
            "tags",
            "recommended_styles",
            "recommended_style_ids",
            "preview_image_url",
            "is_builtin",
            "is_public",
            "is_featured",
            "created_by_username",
            "parent",
            "created_at",
            "updated_at",
            # Favorite fields
            "is_favorited",
            "favorites_count",
        ]

    def get_preview_image_url(self, obj):
        request = self.context.get("request")
        if obj.preview_image and request:
            try:
                return request.build_absolute_uri(obj.preview_image.url)
            except Exception:
                pass
        return None

    def get_is_favorited(self, obj):
        """Whether the requesting user has favorited this theme"""
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return ThemeFavorite.objects.filter(user=user, theme=obj).exists()

    def get_favorites_count(self, obj):
        """Total number of users who have favorited this theme"""
        return ThemeFavorite.objects.filter(theme=obj).count()
