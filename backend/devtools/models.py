from django.db import models

class DevLog(models.Model):
    """Simple log entry for developer actions."""

    event = models.CharField(max_length=120)
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    success = models.BooleanField(default=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.event} @ {self.created_at:%Y-%m-%d %H:%M}"
