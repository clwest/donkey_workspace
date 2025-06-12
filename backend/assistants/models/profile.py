from django.db import models
from django.conf import settings
from .assistant import Assistant
import uuid


class AssistantUserProfile(models.Model):
    """Store user-specific setup metadata for an assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.OneToOneField(
        Assistant, on_delete=models.CASCADE, related_name="user_profile"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assistant_profiles",
    )
    world = models.CharField(max_length=100, blank=True)
    archetype = models.CharField(max_length=100, blank=True)
    glossary_tags = models.JSONField(default=list, blank=True)
    intro_memory_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Profile for {self.assistant.name}"
