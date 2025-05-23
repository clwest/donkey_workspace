from django.db import models


class AdaptiveLoopConfig(models.Model):
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    trigger_conditions = models.JSONField()
    reflection_frequency_days = models.IntegerField()
    learning_targets = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class LearningTrailNode(models.Model):
    """Narrative checkpoint representing an assistant's symbolic learning step."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    archetype = models.CharField(max_length=100)
    learning_vector = models.JSONField()
    symbolic_trigger = models.TextField()
    success = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
