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
