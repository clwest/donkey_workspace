from django.db import models


class AdaptiveLoopConfig(models.Model):
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    metric_name = models.CharField(max_length=100)
    threshold = models.FloatField()
    adjustment = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
