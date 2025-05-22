from django.db import models
from assistants.models.assistant import Assistant


class MythologyMeshNode(models.Model):
    """Graph node linking assistants by mythic relationships."""

    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name="mesh_nodes",
    )
    connected_to = models.ManyToManyField(
        Assistant,
        related_name="mesh_links",
        blank=True,
    )
    link_reason = models.JSONField(default=dict)
    mythic_distance_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)


class ArchetypalDriftForecast(models.Model):
    """Prediction of an assistant's future archetype."""

    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name="drift_forecasts",
    )
    observed_archetype = models.CharField(max_length=100)
    predicted_archetype = models.CharField(max_length=100)
    drift_score = models.FloatField(default=0.0)
    prediction_basis = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
