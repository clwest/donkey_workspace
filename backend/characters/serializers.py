from rest_framework import serializers
from .models import (
    CharacterProfile,
    CharacterStyle,
    CharacterReferenceImage,
    CharacterTag,
    CharacterTrainingProfile,
)
from images.models import PromptHelper, TagImage
from images.serializers import PromptHelperSerializer
from images.serializers import ImageSerializer
from project.models import Project


class CharacterTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterTag
        fields = ["id", "name"]


class TagImageSerializer(serializers.ModelSerializer):
    """Serializer for semantic tags on reference images"""

    class Meta:
        model = TagImage
        fields = ["name"]


class CharacterReferenceImageSerializer(serializers.ModelSerializer):
    # Include character ID (write-only) and handle image uploads or URLs
    character = serializers.PrimaryKeyRelatedField(
        queryset=CharacterProfile.objects.all(), write_only=True
    )
    # Use URL for image field and include caption and alt_text
    image = serializers.ImageField(use_url=True)

    # Expose character slug for frontend gallery routing
    character_slug = serializers.SerializerMethodField()
    # Semantic tags extracted for this image
    tags = TagImageSerializer(many=True, read_only=True)
    # Visual style of this reference image
    style = PromptHelperSerializer(read_only=True)
    # Accept style selection by ID
    style_id = serializers.PrimaryKeyRelatedField(
        queryset=PromptHelper.objects.all(),
        source="style",
        write_only=True,
        required=False,
        allow_null=True,
    )
    # Mark as primary reference image
    is_primary = serializers.BooleanField(required=False)

    def get_character_slug(self, obj):
        return obj.character.slug

    class Meta:
        model = CharacterReferenceImage
        fields = [
            "id",
            "character",
            "character_slug",
            "image",
            "caption",
            "alt_text",
            "created_at",
            "tags",
            "style",
            "style_id",
            "is_primary",
        ]


class PromptHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptHelper
        fields = [
            "id",
            "name",
            "description",
            "prompt",
            "negative_prompt",
        ]


class CharacterStyleSerializer(serializers.ModelSerializer):
    # Nested prompt helper data and absolute image reference URL
    image_reference = serializers.ImageField(use_url=True)
    prompt_helper = PromptHelperSerializer(read_only=True)

    class Meta:
        model = CharacterStyle
        fields = [
            "id",
            "style_name",
            "prompt",
            "negative_prompt",
            "image_reference",
            "prompt_helper",
        ]


class CharacterProfileSerializer(serializers.ModelSerializer):
    # Include slug and primary image URL for frontend deep-linking and preview
    slug = serializers.CharField(read_only=True)
    image_url = serializers.SerializerMethodField()
    styles = CharacterStyleSerializer(many=True, read_only=True)
    # Multiple preferred visual styles per character
    character_styles = PromptHelperSerializer(many=True, read_only=True)
    # Accept visual style selections by ID
    character_style_ids = serializers.PrimaryKeyRelatedField(
        queryset=PromptHelper.objects.all(),
        many=True,
        write_only=True,
        source="character_styles",
    )
    reference_images = CharacterReferenceImageSerializer(many=True, read_only=True)
    tags = CharacterTagSerializer(many=True, read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), required=False, allow_null=True
    )
    # Include training status of the embedding task
    training_status = serializers.SerializerMethodField()
    # Include generated scene images for this character
    scene_images = serializers.SerializerMethodField()

    def get_training_status(self, obj):
        if hasattr(obj, "training_profile"):
            return obj.training_profile.status
        return "not_started"

    def get_scene_images(self, obj):
        """Return completed scene-based images generated for this character."""
        from images.models import Image as SceneImage

        scenes = SceneImage.objects.filter(
            character=obj, generation_type="scene", status="completed"
        ).order_by("-completed_at")
        return ImageSerializer(scenes, many=True, context=self.context).data

    class Meta:
        model = CharacterProfile
        # Expose slug and a URL to the primary image for each character
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "personality_traits",
            "backstory",
            "is_public",
            "is_featured",
            "project",
            "tags",
            "styles",
            "character_styles",
            "reference_images",
            "scene_images",
            "image_url",
            "created_by",
            "created_at",
            "training_status",
            "character_style_ids",
        ]

    def get_image_url(self, obj):
        """Return the absolute URL to the primary reference image, or null."""
        img = obj.primary_image
        if not img or not getattr(img, "image", None):
            return None
        try:
            # Get the image URL and build absolute URI if request context available
            url = img.image.url
            request = self.context.get("request")
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None


class CharacterTrainingProfileSerializer(serializers.ModelSerializer):
    # Expose only status and metadata; embedding vectors can be large, so report their length and a small preview
    vector_length = serializers.SerializerMethodField()
    # Provide a brief preview of the embedding (first few values)
    embedding_preview = serializers.SerializerMethodField()

    class Meta:
        model = CharacterTrainingProfile
        fields = [
            "status",
            "vector_length",
            "embedding_preview",
            "created_at",
            "updated_at",
        ]

    def get_vector_length(self, obj):
        # Return the size of the embedding vector, or 0 if missing
        emb = getattr(obj, "embedding", None)
        try:
            return len(emb) if emb is not None else 0
        except Exception:
            return 0

    def get_embedding_preview(self, obj):
        # Return the first 5 elements of the embedding vector as a preview
        emb = getattr(obj, "embedding", None) or []
        try:
            return emb[:5]
        except Exception:
            return []
