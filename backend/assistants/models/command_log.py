from django.db import models
from django.conf import settings

class AssistantCommandLog(models.Model):
    """Record output from a management command run for an assistant."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cli_logs",
    )
    command = models.CharField(max_length=255)
    flags = models.TextField(blank=True)
    output = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="running")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.command} ({self.status})"
