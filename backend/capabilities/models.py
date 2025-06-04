from django.db import models

class CapabilityUsageLog(models.Model):
    """Record when a capability route is used."""

    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="capability_logs",
    )
    capability = models.CharField(max_length=100)
    request_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

