from django.db import models


class SymbolicAgentInsightLog(models.Model):
    """Record symbolic conflicts detected during document ingestion."""

    agent = models.ForeignKey(
        "agents.Agent", on_delete=models.CASCADE, related_name="insight_logs"
    )
    document = models.ForeignKey(
        "intel_core.Document", on_delete=models.CASCADE, related_name="insight_logs"
    )
    symbol = models.CharField(max_length=100)
    conflict_score = models.FloatField(default=0.0)
    resolution_method = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.agent.slug} {self.symbol} conflict"
