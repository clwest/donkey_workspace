import uuid
from django.db import models

from assistants.models.assistant import Assistant


class TaskAssignment(models.Model):
    """Simple task assignment from one assistant to another."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name="task_assignments_made",
    )
    to_assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name="task_assignments_received",
    )
    description = models.TextField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.from_assistant} -> {self.to_assistant}: {self.description[:20]}"
