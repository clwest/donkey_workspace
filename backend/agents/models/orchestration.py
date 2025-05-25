from django.db import models


class AssistantOrchestrationEvent(models.Model):
    """Track assistant actions for orchestration timeline."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    event_type = models.CharField(max_length=100)
    clause = models.CharField(max_length=100, blank=True)
    context = models.JSONField(blank=True, default=dict)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]


class OrchestrationTimelineSnapshot(models.Model):
    """Daily snapshot of orchestration events."""

    snapshot_date = models.DateField()
    events = models.ManyToManyField(AssistantOrchestrationEvent)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-snapshot_date"]
