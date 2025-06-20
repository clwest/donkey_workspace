from django.db import models
from django.conf import settings
from django.utils import timezone


class AssistantHintState(models.Model):
    """Track whether a user has seen or dismissed a specific hint."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    hint_id = models.CharField(max_length=100)
    sequence_index = models.IntegerField(
        null=True,
        blank=True,
        help_text="Position of this hint in the tour sequence",
    )
    dismissed = models.BooleanField(default=False)
    seen_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "assistant", "hint_id"]
        ordering = ["-seen_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.user.username}:{self.assistant.slug}:{self.hint_id}"
