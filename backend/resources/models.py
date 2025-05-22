from django.db import models


class ResourcePrediction(models.Model):
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    predicted_tokens = models.IntegerField()
    predicted_compute_ms = models.FloatField()
    prediction_time = models.DateTimeField(auto_now_add=True)


class ResourceBudget(models.Model):
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    allocated_tokens = models.IntegerField()
    allocated_compute_ms = models.FloatField()
    used_tokens = models.IntegerField(default=0)
    used_compute_ms = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
