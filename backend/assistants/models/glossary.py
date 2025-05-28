import uuid
from django.db import models


class AssistantGlossaryLog(models.Model):
    """Record cases where glossary context was injected but ignored."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    anchor = models.ForeignKey(
        "memory.SymbolicMemoryAnchor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="glossary_logs",
    )
    query = models.TextField()
    ignored = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Glossary log for {self.assistant}"

