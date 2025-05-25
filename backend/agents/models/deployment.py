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



class AssistantDeploymentLog(models.Model):
    """Record assistant deployments across environments."""

    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    label = models.CharField(max_length=150)
    environment = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant.slug} -> {self.environment}"


class DeploymentVector(models.Model):
    """Symbolic deployment target descriptor."""

    task = models.CharField(max_length=150)
    codex = models.CharField(max_length=150)
    ritual = models.CharField(max_length=150)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.task}/{self.codex}/{self.ritual}"


class ToolAssignment(models.Model):
    """Selected tools for an assistant deployment."""

    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    tools = models.ManyToManyField('tools.Tool')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"Tools for {self.assistant.slug}"


class SymbolicToolMap(models.Model):
    """Map skills or symbols to tools."""

    skill = models.CharField(max_length=150)
    tool = models.ForeignKey('tools.Tool', on_delete=models.CASCADE)
    weight = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.skill} -> {self.tool.slug}"


class AgentExecutionSession(models.Model):
    """Track a run of assistant + toolchain."""

    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    toolchain = models.JSONField(default=list)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"Session {self.id} ({self.status})"


class PromptExecutionTrace(models.Model):
    """Record each prompt executed in a session."""

    session = models.ForeignKey(AgentExecutionSession, on_delete=models.CASCADE, related_name='traces')
    prompt = models.TextField()
    result = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"Trace {self.id} ({'ok' if self.success else 'fail'})"


class ToolOutcomeLedger(models.Model):
    """Outcome logs for tool executions in a session."""

    session = models.ForeignKey(AgentExecutionSession, on_delete=models.CASCADE, related_name='tool_outcomes')
    tool = models.ForeignKey('tools.Tool', on_delete=models.CASCADE)
    payload = models.JSONField(default=dict)
    result = models.JSONField(null=True, blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.tool.slug} ({'ok' if self.success else 'fail'})"


# === Recovery Hook ===
from django.db.models.signals import post_save
from django.dispatch import receiver


def trigger_recovery_handler(trace):
    """Placeholder recovery handler for failed executions."""
    print(f"Recovery triggered for trace {trace.id}")


@receiver(post_save, sender=PromptExecutionTrace)
def handle_failed_prompt(sender, instance, created, **kwargs):
    if created and not instance.success:
        trigger_recovery_handler(instance)
class DeploymentEventTag(models.Model):
    """Tag for deployment narrative events."""

    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.name


class DeploymentNarrativeLog(models.Model):
    """Narrative record of a deployment evaluation."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    project = models.CharField(max_length=150, blank=True)
    ritual_type = models.CharField(max_length=150, blank=True)
    belief_tags = models.JSONField(default=list, blank=True)
    narrative = models.TextField(blank=True)
    events = models.ManyToManyField(DeploymentEventTag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant.slug} narrative"


class CodexAlignmentSnapshot(models.Model):
    """Alignment snapshot for a codex clause during deployment."""

    deployment_log = models.ForeignKey(
        DeploymentNarrativeLog, on_delete=models.CASCADE, related_name="snapshots"
    )
    codex_clause = models.CharField(max_length=150)
    alignment_score = models.FloatField(default=0.0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.codex_clause


class DeploymentReplayTrace(models.Model):
    """Replay a deployment vector for analysis."""

    vector = models.ForeignKey(DeploymentVector, on_delete=models.CASCADE)
    original_log = models.ForeignKey(
        DeploymentNarrativeLog, null=True, blank=True, on_delete=models.SET_NULL
    )
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    output = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Replay {self.vector_id}"


class EvaluationMutationFork(models.Model):
    """Track mutations when replaying an evaluation."""

    replay_trace = models.ForeignKey(
        DeploymentReplayTrace, on_delete=models.CASCADE, related_name="mutations"
    )
    new_assistant = models.ForeignKey(
        "assistants.Assistant", null=True, blank=True, on_delete=models.SET_NULL
    )
    modified_clause = models.TextField(blank=True)
    output_diff = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Mutation {self.id}"


class PromptDeltaReport(models.Model):
    """Diff report for prompt mutations in a replay."""

    mutation_fork = models.ForeignKey(
        EvaluationMutationFork, on_delete=models.CASCADE, related_name="deltas"
    )
    delta_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Delta {self.id}"


class AssistantFeedbackLoopVector(models.Model):
    """Stats driving iteration suggestions."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    retry_failures = models.IntegerField(default=0)
    misalignment_count = models.IntegerField(default=0)
    token_cost = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Feedback vector for {self.assistant.slug}"


class DeploymentIterationSuggestion(models.Model):
    """Suggested improvements for a deployment."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    suggestion = models.TextField()
    confidence = models.FloatField(default=0.0)
    symbolic_gain = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.suggestion[:50]
