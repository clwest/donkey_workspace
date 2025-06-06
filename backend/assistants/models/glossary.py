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


class SuggestionLog(models.Model):
    """Store drift-based glossary suggestions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="drift_suggestions",
    )
    trigger_type = models.CharField(max_length=50, default="first_message_drift")
    anchor_slug = models.CharField(max_length=100, blank=True, null=True)
    suggested_action = models.CharField(max_length=50)
    score = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.assistant} {self.anchor_slug} {self.suggested_action}"
