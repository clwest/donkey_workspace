from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class AssistantUserPreferences(models.Model):
    """Store user-specific preferences for an assistant."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="user_preferences",
    )
    tone = models.CharField(max_length=50, default="friendly")
    planning_mode = models.CharField(max_length=50, default="short_term")
    custom_tags = ArrayField(models.CharField(max_length=64), blank=True, default=list)
    self_narration_enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "assistant")
        ordering = ["assistant"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.user} -> {self.assistant}"
