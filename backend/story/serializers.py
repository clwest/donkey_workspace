from rest_framework import serializers
from story.models import Story, NarrativeEvent, LoreEntry
from images.serializers import ImageSerializer
from tts.serializers import StoryAudioSerializer
from images.models import PromptHelper
from images.serializers import PromptHelperSerializer
from characters.models import CharacterProfile
from characters.serializers import CharacterProfileSerializer


class StorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    image = ImageSerializer(read_only=True)
    tts = StoryAudioSerializer(read_only=True)
    tts_preview_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    image_caption = serializers.CharField(read_only=True)
    image_alt_text = serializers.CharField(read_only=True)
    # Nested visual style override
    style = PromptHelperSerializer(read_only=True)
    # Accept style override by ID
    style_id = serializers.PrimaryKeyRelatedField(
        queryset=PromptHelper.objects.all(),
        source="style",
        write_only=True,
        required=False,
        allow_null=True,
    )
    story_images = ImageSerializer(many=True, read_only=True)
    # Nested character info (read-only) and accept character selection by ID (write-only)
    character = CharacterProfileSerializer(read_only=True)
    character_id = serializers.PrimaryKeyRelatedField(
        queryset=CharacterProfile.objects.all(),
        source="character",
        write_only=True,
        required=False,
        allow_null=True,
    )
    # Optionally link multiple characters by IDs
    characters = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CharacterProfile.objects.all(), required=False
    )

    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = [
            "user",
            "project",
            "generated_text",
            "image",
            "tts",
            "tts_preview_url",
            "image_url",
            "image_caption",
            "image_alt_text",
            "created_at",
            "updated_at",
        ]

    def get_tts_preview_url(self, obj):
        request = self.context.get("request")
        if obj.tts and obj.tts.audio_file:
            return (
                request.build_absolute_uri(obj.tts.audio_file.url)
                if request
                else obj.tts.audio_file.url
            )
        return None


class NarrativeEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = NarrativeEvent
        fields = [
            "id",
            "title",
            "description",
            "scene_summary",
            "summary_generated",
            "timestamp",
            "project",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and obj.image.output_url:
            return (
                request.build_absolute_uri(obj.image.output_url)
                if request
                else obj.image.output_url
            )
        return None


class StoryDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    image = ImageSerializer(read_only=True)
    tts = StoryAudioSerializer(read_only=True)
    tts_preview_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    story_images = ImageSerializer(many=True, source="illustrations")

    # Nested visual style in detail view
    style = PromptHelperSerializer(read_only=True)
    # Nested character info if linked
    character = CharacterProfileSerializer(read_only=True)

    class Meta:
        model = Story
        # Include linked character and optional multiple characters
        fields = [
            "id",
            "title",
            "theme",
            "generated_text",
            "image",
            "image_url",
            "tts",
            "tts_preview_url",
            "style",
            "status",
            "project",
            "character",
            "characters",
            "story_images",
            "user",
        ]

    def get_tts_preview_url(self, obj):
        request = self.context.get("request")
        if obj.tts and obj.tts.audio_file:
            return (
                request.build_absolute_uri(obj.tts.audio_file.url)
                if request
                else obj.tts.audio_file.url
            )
        return None


class LoreEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoreEntry
        fields = [
            "id",
            "title",
            "content",
            "tone",
            "epithets",
            "traits",
            "lineage",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
