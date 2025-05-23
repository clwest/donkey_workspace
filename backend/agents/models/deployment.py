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
class GuildDeploymentKit(models.Model):
    """Portable belief package configured for a guild."""

    guild = models.ForeignKey(
        'assistants.CodexLinkedGuild', on_delete=models.CASCADE
    )
    included_codices = models.ManyToManyField(SwarmCodex)
    assistant_manifest = models.ManyToManyField('assistants.Assistant')
    symbolic_parameters = models.JSONField()
    deployment_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"Deployment kit for {self.guild.guild_name}"


class AssistantNetworkTransferProtocol(models.Model):
    """Transfer assistant state between symbolic networks."""

    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    source_network = models.CharField(max_length=150)
    target_network = models.CharField(max_length=150)
    symbolic_transfer_packet = models.JSONField()
    codex_compatibility_log = models.TextField()
    successful_transfer_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"Transfer {self.assistant.name} to {self.target_network}"


class RitualFunctionContainer(models.Model):
    """Containerized ritual execution with state persistence."""

    ritual = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE)
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    execution_context = models.JSONField()
    symbolic_input_log = models.JSONField()
    result_trace = models.TextField()
    container_status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"Container for {self.ritual.name}"


class MythOSReplicationBlueprint(models.Model):
    """Hash-verifiable blueprint for MythOS replication."""

    blueprint_title = models.CharField(max_length=150)
    included_codices = models.ManyToManyField(SwarmCodex)
    assistant_manifest = models.ManyToManyField("assistants.Assistant")
    ritual_seed_set = models.ManyToManyField(EncodedRitualBlueprint)
    deployment_signature = models.TextField()
    symbolic_fingerprint_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.blueprint_title


class BeliefAlignedDeploymentStandard(models.Model):
    """Criteria for launching MythOS with symbolic fidelity."""

    target_environment = models.CharField(max_length=150)
    codex_affinity_threshold = models.FloatField()
    ritual_readiness_index = models.FloatField()
    assistant_compatibility_map = models.JSONField()
    symbolic_convergence_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.target_environment


class ReflectiveIntelligenceProtocolRegistry(models.Model):
    """Registry for decentralized reflective intelligence settings."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    reflective_cluster_id = models.CharField(max_length=150)
    memory_feedback_cycle = models.JSONField()
    codex_drift_strategy = models.TextField()
    narrative_loop_regulator = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Protocol {self.reflective_cluster_id}"

