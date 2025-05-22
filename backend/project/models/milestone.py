import uuid
from django.db import models
from .core import Project


class MilestoneStatus(models.TextChoices):
    PLANNED = "Planned", "Planned"
    IN_PROGRESS = "In Progress", "In Progress"
    COMPLETED = "Completed", "Completed"


class ProjectMilestone(models.Model):
    """Milestone for a project with due dates and status."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=MilestoneStatus.choices, default=MilestoneStatus.PLANNED
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "created_at"]

    @property
    def is_completed(self) -> bool:
        """Return True if the milestone status denotes completion."""
        return self.status == MilestoneStatus.COMPLETED

    def __str__(self) -> str:
        return f"{self.title} ({'Done' if self.is_completed else 'Pending'})"
