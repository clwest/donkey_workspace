from django.db import models

class AssistantDevLog(models.Model):
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="dev_logs"
    )
    issue_type = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant.slug} {self.issue_type}"
