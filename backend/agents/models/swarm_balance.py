from django.db import models


class SymbolicResonanceGraph(models.Model):
    """Cross-assistant symbolic resonance mapping."""

    scope = models.CharField(max_length=100)
    nodes = models.JSONField()
    edges = models.JSONField()
    resonance_map = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]


class CognitiveBalanceReport(models.Model):
    """Diagnostic report for swarm cognitive load."""

    guild = models.ForeignKey(
        "assistants.AssistantGuild", on_delete=models.CASCADE, related_name="balance_reports"
    )
    entropy_index = models.FloatField()
    symbolic_pressure_zones = models.JSONField()
    recommendations = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PurposeMigrationEvent(models.Model):
    """Record of intent handoff between assistants."""

    reassigned_from = models.ForeignKey(
        "assistants.Assistant",
        related_name="migration_outbound",
        on_delete=models.CASCADE,
    )
    reassigned_to = models.ForeignKey(
        "assistants.Assistant",
        related_name="migration_inbound",
        on_delete=models.CASCADE,
    )
    intent_vector = models.JSONField()
    migration_reason = models.TextField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
