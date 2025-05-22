import uuid
from django.db import models
from .core import Project


class TaskStatus(models.TextChoices):
    TODO = "todo", "To Do"
    IN_PROGRESS = "in_progress", "In Progress"
    DONE = "done", "Done"


class ProjectTask(models.Model):
    """Task associated with a :class:`Project`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, related_name="core_tasks", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    content = models.TextField()
    status = models.CharField(
        max_length=50, choices=TaskStatus.choices, default=TaskStatus.TODO
    )
    priority = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"[{self.status.upper()}] {self.title}"
