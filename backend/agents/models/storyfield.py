from django.db import models

from .lore import SwarmMemoryEntry


class StoryfieldZone(models.Model):
    """Interactive narrative layer tuned to assistant archetypes."""

    zone_name = models.CharField(max_length=150)
    aligned_roles = models.JSONField()
    myth_tags = models.JSONField()
    active_memory = models.ManyToManyField(SwarmMemoryEntry)
    resonance_threshold = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class MythPatternCluster(models.Model):
    """Recurring mythic motif or reflected narrative pattern."""

    cluster_id = models.CharField(max_length=100)
    pattern_summary = models.TextField()
    linked_memories = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_signature = models.CharField(max_length=256)
    convergence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class IntentHarmonizationSession(models.Model):
    """Multi-agent purpose calibration session within a symbolic scenario."""

    involved_assistants = models.ManyToManyField("assistants.Assistant")
    coordination_focus = models.TextField()
    proposed_strategies = models.JSONField()
    symbolic_alignment_score = models.FloatField()
    consensus_reached = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class NarrativeTrainingGround(models.Model):
    """Simulated training environment for belief or narrative performance."""

    training_title = models.CharField(max_length=150)
    involved_assistants = models.ManyToManyField("assistants.Assistant")
    scenario_description = models.TextField()
    target_archetypes = models.JSONField()
    memory_feed = models.ManyToManyField(SwarmMemoryEntry)
    evaluation_results = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class SwarmMythEditLog(models.Model):
    """Track collaborative story edits and symbolic shifts."""

    edit_summary = models.TextField()
    affected_myth = models.ForeignKey(
        "agents.TranscendentMyth", on_delete=models.CASCADE
    )
    editor_assistants = models.ManyToManyField("assistants.Assistant")
    before_state = models.TextField()
    after_state = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class LegacyContinuityVault(models.Model):
    """Archive preserved archetypes and codex snapshots."""

    vault_name = models.CharField(max_length=150)
    preserved_archetypes = models.JSONField()
    assistant_snapshots = models.ManyToManyField("agents.SymbolicIdentityCard")
    codex_archives = models.ManyToManyField("agents.SwarmCodex")
    narrative_epoch = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
