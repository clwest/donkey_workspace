from django.db import models


class PerformanceMetric(models.Model):
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class RitualPerformanceMetric(models.Model):
    """Tracks symbolic resonance and transformation alignment for ritual events."""

    ritual = models.ForeignKey(
        'agents.RitualArchiveEntry', on_delete=models.CASCADE
    )
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    symbolic_score = models.FloatField()
    transformation_alignment = models.FloatField()
    mythic_tags = models.JSONField()
    reflection_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
