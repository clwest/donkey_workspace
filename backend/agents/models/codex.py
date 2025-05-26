from django.db import models


class CodexClause(models.Model):
    """Simple codex clause used for stabilization campaigns."""

    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Clause {self.id}"

