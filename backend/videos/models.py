from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings


class Video(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="runway_videos"
    )
    prompt = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to="runway_outputs/", blank=True, null=True)
    input_image = models.ImageField(upload_to="runway_inputs/", blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    provider = models.CharField(max_length=50, default="runway-gen4")

    # 🧩 Connections
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="videos",
    )
    story = models.ForeignKey(
        "story.Story",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="runway_clips",
    )
    # If this video is tied to a specific paragraph in the story (scene index)
    paragraph_index = models.IntegerField(
        null=True,
        blank=True,
        help_text="If this video is for a specific paragraph in the story",
    )

    # 💬 Metadata
    caption = models.CharField(max_length=255, blank=True, null=True)
    duration_seconds = models.FloatField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    video_style = models.CharField(max_length=100, blank=True, null=True)
    output_format = models.CharField(max_length=20, default="mp4")
    resolution = models.CharField(max_length=20, default="1024x1024")

    theme = models.CharField(max_length=100, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    # Backend selection for video generation
    MODEL_BACKEND_CHOICES = [
        ("stability", "Stability.ai (SDXL)"),
        ("replicate-standard", "Replicate - Standard Image"),
        ("replicate-kling", "Replicate - Kling v1.6 Video"),
        ("openai", "OpenAI (DALL-E or Whisper)"),
    ]
    model_backend = models.CharField(
        max_length=50,
        choices=MODEL_BACKEND_CHOICES,
        default="stability",
        help_text="Select which backend model to use for generation",
    )
    # External prediction job ID and error storage
    prediction_id = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return self.prompt[:50]
