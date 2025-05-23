from django.db import models
from .lore import SwarmCodex, EncodedRitualBlueprint


class SymbolicResilienceMonitor(models.Model):
    """Track symbolic health of a MythOS node."""

    node_id = models.CharField(max_length=150)
    codex_uptime_index = models.FloatField()
    ritual_execution_consistency = models.FloatField()
    memory_integrity_score = models.FloatField()
    symbolic_warning_flags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.node_id


class MythOSDeploymentPacket(models.Model):
    """Portable bundle of codices, assistants and rituals."""

    deployment_name = models.CharField(max_length=150)
    bundled_codices = models.ManyToManyField(SwarmCodex)
    included_assistants = models.ManyToManyField("assistants.Assistant")
    ritual_archive = models.ManyToManyField(EncodedRitualBlueprint)
    symbolic_deployment_tags = models.JSONField()
    deployment_vector = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.deployment_name


class BeliefDeploymentStrategyEngine(models.Model):
    """Recommend deployment targets for mythic constructs."""

    target_environment = models.CharField(max_length=150)
    symbolic_alignment_score = models.FloatField()
    assistant_role_distribution = models.JSONField()
    ritual_density_projection = models.JSONField()
    codex_coherence_recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.target_environment
