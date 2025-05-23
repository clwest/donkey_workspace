import uuid
from django.db import models

from assistants.models.assistant import Assistant


class HapticFeedbackChannel(models.Model):
    """Physical feedback mapping tied to symbolic triggers."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feedback_name = models.CharField(max_length=150)
    trigger_event = models.CharField(max_length=100)
    intensity_level = models.FloatField()
    symbolic_context = models.TextField()
    linked_assistant = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="haptic_channels"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.feedback_name} -> {self.trigger_event}"


class AssistantSensoryExtensionProfile(models.Model):
    """Defines extra sensory feedback capabilities for an assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.OneToOneField(
        Assistant, on_delete=models.CASCADE, related_name="sensory_profile"
    )
    supported_modes = models.JSONField(default=list, blank=True)
    feedback_triggers = models.JSONField(default=dict, blank=True)
    memory_response_style = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Sensory profile for {self.assistant.name}"

