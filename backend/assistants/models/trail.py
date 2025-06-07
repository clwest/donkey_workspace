import uuid
from django.db import models


class TrailMarkerLog(models.Model):
    """Milestone marker for an assistant's lifecycle."""

    class MarkerType(models.TextChoices):
        BIRTH = "birth", "Birth"
        PERSONALIZATION = "personalization", "Personalization"
        FIRST_CHAT = "first_chat", "First Chat"
        FIRST_REFLECTION = "first_reflection", "First Reflection"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="trail_markers",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    marker_type = models.CharField(max_length=50, choices=MarkerType.choices)
    related_memory = models.ForeignKey(
        "memory.MemoryEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trail_markers",
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant.name} - {self.marker_type}"
