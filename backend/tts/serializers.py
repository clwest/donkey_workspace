from rest_framework import serializers
from tts.models import StoryAudio, SceneAudio


class StoryAudioSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    # Generation backend: stability (SDXL), replicate, or openai
    model_backend = serializers.ChoiceField(
        choices=StoryAudio.MODEL_BACKEND_CHOICES,
        default=StoryAudio.MODEL_BACKEND_CHOICES[0][0],
        help_text="Audio generation backend to use",
    )

    class Meta:
        model = StoryAudio
        fields = [
            "id",
            "prompt",
            "voice_style",
            "provider",
            "model_backend",
            "status",
            "audio_url",
            "base64_audio",
            "created_at",
            "user",
        ]
        read_only_fields = [
            "audio_url",
            "base64_audio",
            "created_at",
            "user",
            "status",
        ]

    def get_audio_url(self, obj):
        request = self.context.get("request")
        if obj.audio_file and hasattr(obj.audio_file, "url"):
            return (
                request.build_absolute_uri(obj.audio_file.url)
                if request
                else obj.audio_file.url
            )
        return None


class SceneAudioSerializer(serializers.ModelSerializer):
    """Serializer for TTS narration of scene images"""

    audio_url = serializers.SerializerMethodField()
    image = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SceneAudio  # noqa: F821
        fields = [
            "id",
            "image",
            "prompt",
            "voice_style",
            "provider",
            "status",
            "audio_url",
            "base64_audio",
            "task_id",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "audio_url",
            "base64_audio",
            "task_id",
            "created_at",
        ]

    def get_audio_url(self, obj):
        request = self.context.get("request")
        if obj.audio_file and hasattr(obj.audio_file, "url"):
            return (
                request.build_absolute_uri(obj.audio_file.url)
                if request
                else obj.audio_file.url
            )
        return None
