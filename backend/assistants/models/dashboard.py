from django.db import models


class AssistantDashboardNotification(models.Model):
    """Alert generated for an assistant dashboard panel."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)
    message = models.TextField()
    related_memory = models.ForeignKey(
        "agents.SwarmMemoryEntry", on_delete=models.SET_NULL, null=True, blank=True
    )
    related_ceremony = models.ForeignKey(
        "agents.CodexContributionCeremony", on_delete=models.SET_NULL, null=True, blank=True
    )
    related_directive = models.ForeignKey(
        "agents.DirectiveMemoryNode", on_delete=models.SET_NULL, null=True, blank=True
    )
    related_metric = models.ForeignKey(
        "metrics.RitualPerformanceMetric", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.alert_type} for {self.assistant.name}"


class CodexStateAlert(models.Model):
    """Snapshot of codex stress and alignment metrics."""

    codex = models.ForeignKey("agents.SwarmCodex", on_delete=models.CASCADE)
    entropy_level = models.FloatField()
    coherence_index = models.FloatField()
    alignment_drift = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Alert for {self.codex.title}"


class RitualStatusBeacon(models.Model):
    """Live ritual status indicator tied to an assistant."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    ritual_blueprint = models.ForeignKey("agents.EncodedRitualBlueprint", on_delete=models.CASCADE)
    availability_state = models.CharField(max_length=20)
    entropy_level = models.FloatField()
    alignment_readiness = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Beacon {self.ritual_blueprint.name} ({self.availability_state})"
