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


class AssistantRehydrationPipeline(models.Model):
    """Resurrect assistants from archived mythic state."""

    assistant_archive_id = models.CharField(max_length=150)
    rehydration_source = models.TextField()
    memory_rebind_trace = models.JSONField()
    codex_state_applied = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    assistant_rehydrated_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.assistant_archive_id


class RitualExecutionOrchestrationLog(models.Model):
    """Full trace of ritual execution across nodes."""

    ritual = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE)
    orchestrator_id = models.CharField(max_length=150)
    execution_path = models.JSONField()
    symbolic_disruption_flags = models.JSONField()
    codex_sync_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Log for {self.ritual.name}"


class SymbolicReplayEngine(models.Model):
    """Replay mythic scenarios across distributed networks."""

    replay_id = models.CharField(max_length=150)
    source_network = models.CharField(max_length=150)
    symbolic_inputs = models.JSONField()
    assistant_context = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    replay_result = models.TextField()
    entropy_convergence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.replay_id
