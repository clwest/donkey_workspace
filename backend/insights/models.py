from django.db import models
from django.conf import settings


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


class AssistantInsightLog(models.Model):
    """Store high level insights from chat reflections."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="insight_logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assistant_insights",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    log_type = models.CharField(max_length=50, default="reflection")
    tags = models.JSONField(default=list, blank=True)
    summary = models.TextField()
    proposed_prompt = models.TextField(null=True, blank=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant.slug} insight {self.created_at:%Y-%m-%d}"
