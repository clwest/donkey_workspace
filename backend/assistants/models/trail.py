import uuid
from django.db import models


class TrailMarkerLog(models.Model):
    """Milestone marker for an assistant's lifecycle."""

    class MarkerType(models.TextChoices):
        BIRTH = "birth", "Birth"
        PERSONALIZATION = "personalization", "Personalization"
        FIRST_CHAT = "first_chat", "First Chat"
        FIRST_REFLECTION = "first_reflection", "First Reflection"
        DEMO_CONVERTED = "demo_converted", "Demo Converted"

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
    user_note = models.TextField(null=True, blank=True)
    user_emotion = models.CharField(max_length=16, null=True, blank=True)
    is_starred = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant.name} - {self.marker_type}"

    def get_emotion_display(self):  # pragma: no cover - simple accessor
        """Return the emoji representation of the stored emotion."""
        return self.user_emotion or ""
