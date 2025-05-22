from django.db import models


class WorkflowDefinition(models.Model):
    name = models.CharField(max_length=150)
    steps = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover - debug helper
        return self.name


class WorkflowExecutionLog(models.Model):
    workflow = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    log = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
