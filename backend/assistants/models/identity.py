from django.db import models
from .assistant import Assistant


class IdentityAnchor(models.Model):
    """Persistent mythic fingerprint linked to an assistant."""

    assistant = models.OneToOneField(
        Assistant, on_delete=models.CASCADE, related_name="identity_anchor"
    )
    codex_vector = models.JSONField(default=dict, blank=True)
    memory_origin = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"IdentityAnchor for {self.assistant.name}"
