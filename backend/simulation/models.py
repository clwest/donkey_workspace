from django.db import models


class SimulationConfig(models.Model):
    name = models.CharField(max_length=150)
    assistant_ids = models.JSONField()
    scenario_description = models.TextField()
    parameters = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class SimulationRunLog(models.Model):
    config = models.ForeignKey(SimulationConfig, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    log_details = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
