from django.db import models
from django.utils import timezone
from django.conf import settings


class DemoUsageLog(models.Model):
    """Tracks how users interact with demo assistants."""

    session_id = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    demo_slug = models.CharField(max_length=100)
    comparison_variant = models.CharField(max_length=50, blank=True)
    feedback_text = models.TextField(blank=True)
    user_rating = models.IntegerField(null=True, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    recap_shown = models.BooleanField(default=False)
    feedback_submitted = models.BooleanField(default=False)
    reflection = models.ForeignKey(
        "assistants.AssistantReflectionLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    converted_at = models.DateTimeField(null=True, blank=True)
    converted_from_demo = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.demo_slug}:{self.session_id}"
