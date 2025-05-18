from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


class StoryAudio(models.Model):
    TTS_PROVIDERS = (
        ("openai", "OpenAI"),
        ("elevenlabs", "ElevenLabs"),
    )

    TTS_STATUSES = (
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    prompt = models.TextField()
    base64_audio = models.TextField(
        blank=True, null=True
    )  # optional: base64 for frontend preview
    audio_file = models.FileField(upload_to="tts_audio/", blank=True, null=True)

    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tts_audios",
    )
    story = models.OneToOneField(
        "story.Story",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tts_audio",
    )

    voice_style = models.CharField(
        max_length=100, blank=True, null=True
    )  # e.g. echo, nova, or Eleven voice ID
    provider = models.CharField(max_length=20, choices=TTS_PROVIDERS, default="openai")
    status = models.CharField(max_length=20, choices=TTS_STATUSES, default="queued")
    # Backend selection for audio generation
    MODEL_BACKEND_CHOICES = [
        ("stability", "Stability.ai (SDXL)"),
        ("replicate-standard", "Replicate - Standard Image"),
        ("replicate-kling", "Replicate - Kling v1.6 Video"),
        ("openai", "OpenAI"),
    ]
    model_backend = models.CharField(
        max_length=50,
        choices=MODEL_BACKEND_CHOICES,
        default="openai",
        help_text="Select which backend model to use for generation",
    )

    theme = models.CharField(max_length=100, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"TTS for {self.user} | {self.voice_style or 'default'}"


# Scene-specific audio generated for character scenes
class SceneAudio(models.Model):
    """Model for tracking TTS narration of generated scene images."""

    # Reuse provider and status choices from StoryAudio
    TTS_PROVIDERS = StoryAudio.TTS_PROVIDERS
    TTS_STATUSES = StoryAudio.TTS_STATUSES

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scene_audios",
    )
    from images.models import Image as SceneImageModel  # noqa: E402

    image = models.ForeignKey(
        SceneImageModel, on_delete=models.CASCADE, related_name="scene_audios"
    )
    prompt = models.TextField()
    base64_audio = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to="tts_scene_audio/", blank=True, null=True)
    voice_style = models.CharField(max_length=100, blank=True, null=True)
    provider = models.CharField(max_length=20, choices=TTS_PROVIDERS, default="openai")
    status = models.CharField(max_length=20, choices=TTS_STATUSES, default="queued")
    task_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["image"]),
        ]

    def __str__(self):
        return f"SceneAudio for Image {self.image_id} | {self.voice_style or 'default'}"
