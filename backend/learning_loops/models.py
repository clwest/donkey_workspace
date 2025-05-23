from django.db import models


class AdaptiveLoopConfig(models.Model):
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    trigger_conditions = models.JSONField()
    reflection_frequency_days = models.IntegerField()
    learning_targets = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
