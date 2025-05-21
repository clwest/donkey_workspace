from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from images.models import PromptHelper
from characters.models import CharacterProfile


class Story(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("generating", "Generating"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stories"
    )
    title = models.CharField(max_length=200, blank=True)
    prompt = models.TextField()
    summary = models.TextField(blank=True, null=True)
    generated_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional connections to image and TTS
    image = models.ForeignKey(
        "images.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="linked_story",
    )
    cover_image_url = models.URLField(blank=True, null=True)
    tts = models.OneToOneField(
        "tts.StoryAudio",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="linked_story",  # New name
    )
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE,
        related_name="stories",
        null=True,
        blank=True,
    )
    theme = models.CharField(max_length=100, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    published_at = models.DateTimeField(null=True, blank=True)

    # Reward / gamification features
    is_reward = models.BooleanField(default=False)
    reward_reason = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_caption = models.TextField(blank=True, null=True)
    image_alt_text = models.CharField(max_length=300, blank=True, null=True)
    # Style of image to match the story i.e. Fantasy, Anime, Pixar, etc.

    style = models.ForeignKey(
        PromptHelper,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="styled_stories",
    )

    character = models.ForeignKey(
        CharacterProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="legacy_stories",
    )
    # Enable multiple characters per story
    characters = models.ManyToManyField(
        CharacterProfile, related_name="stories", blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return self.title or f"Story {self.id} by {self.user.username}"


class NarrativeEvent(models.Model):
    """Discrete event or milestone in a storyboard or timeline."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="narrative_events",
    )

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.title
