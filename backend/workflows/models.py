from django.db import models


class WorkflowDefinition(models.Model):
    name = models.CharField(max_length=150)
    associated_codex = models.ForeignKey(
        "agents.SwarmCodex", null=True, on_delete=models.SET_NULL
    )
    step_sequence = models.JSONField()
    mythic_rationale = models.TextField()
    created_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover - debug helper
        return self.name


class WorkflowExecutionLog(models.Model):
    workflow = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE)
    triggered_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    execution_data = models.JSONField()
    outcome_summary = models.TextField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
