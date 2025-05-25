from django.db import models


class SwarmAgentRoute(models.Model):
    ROUTE_TYPE_CHOICES = [
        ("mentor", "Mentor"),
        ("relay", "Relay"),
        ("ally", "Ally"),
    ]
    from_assistant = models.ForeignKey(
        "assistants.Assistant", related_name="routes_from", on_delete=models.CASCADE
    )
    to_assistant = models.ForeignKey(
        "assistants.Assistant", related_name="routes_to", on_delete=models.CASCADE
    )
    route_type = models.CharField(max_length=50, choices=ROUTE_TYPE_CHOICES)
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class AgentSymbolicMap(models.Model):
    map_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class RitualRewiringProposal(models.Model):
    """Proposed ritual route adjustments."""

    initiator = models.ForeignKey(
        "assistants.Assistant", related_name="rewire_initiated", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        "assistants.Assistant", related_name="rewire_received", on_delete=models.CASCADE
    )
    context_clause = models.CharField(max_length=150)
    drift_score = models.FloatField(default=0)
    feedback_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
