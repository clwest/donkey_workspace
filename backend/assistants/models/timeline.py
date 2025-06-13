from django.db import models

class AssistantTimelineLog(models.Model):
    """Chronological log for assistant events."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="timeline_logs"
    )
    log_type = models.CharField(max_length=50)
    anchor = models.CharField(max_length=100, blank=True, default="")
    fallback_reason = models.CharField(max_length=100, blank=True, default="")
    query_text = models.TextField(blank=True)
    chunks_retrieved = models.IntegerField(default=0)
    fallback_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant.slug} {self.log_type}" 
