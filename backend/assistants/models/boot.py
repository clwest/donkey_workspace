from django.db import models


class AssistantBootLog(models.Model):
    """Record result of a boot self-test for an assistant."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="boot_logs"
    )
    passed = models.BooleanField()
    report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        status = "PASS" if self.passed else "FAIL"
        return f"{self.assistant.name} {status} @ {self.created_at:%Y-%m-%d}"
