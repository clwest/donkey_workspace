from django.db import models
from django.conf import settings
import uuid


class AssistantTourStartLog(models.Model):
    """Record when a user begins the assistant hint tour."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="tour_start_logs"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, default="dashboard")

    class Meta:
        unique_together = ["user", "assistant"]
        ordering = ["-started_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.user_id}:{self.assistant.slug}@{self.started_at:%Y-%m-%d}"
