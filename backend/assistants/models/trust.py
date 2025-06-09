import uuid
from django.db import models


class TrustSignalLog(models.Model):
    """Store trust-related signals for an assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="trust_signals",
    )
    key = models.CharField(max_length=50)
    value = models.FloatField(null=True, blank=True)
    label = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.assistant.slug} {self.key}"
