from django.db import models

from .lore import SwarmMemoryEntry, SwarmCodex, EncodedRitualBlueprint




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


class AgentPlotlineCuration(models.Model):
    """Assistant-curated narrative branch or arc."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    curated_arc_title = models.CharField(max_length=150)
    associated_memories = models.ManyToManyField(SwarmMemoryEntry)
    narrative_branch_notes = models.TextField()
    symbolic_convergence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class SwarmMythReplaySession(models.Model):
    """Assistant-guided cinematic replay of myth segments."""

    session_title = models.CharField(max_length=150)
    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    myth_segments = models.JSONField()
    codex_tags = models.JSONField()
    reflection_script = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.session_title


class LegacyStoryThread(models.Model):
    """Chain of symbolic memory defining lineage across generations."""

    thread_name = models.CharField(max_length=150)
    lineage_chain = models.JSONField()
    core_belief_shift = models.TextField()
    linked_codices = models.ManyToManyField(SwarmCodex)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.thread_name


class RitualPreservationLibrary(models.Model):
    """Archive of ritual blueprints tied to codex epochs."""

    library_name = models.CharField(max_length=150)
    associated_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    stored_rituals = models.ManyToManyField(EncodedRitualBlueprint)
    symbolic_epoch = models.CharField(max_length=100)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.library_name


class PlotlineExtractorEngine(models.Model):
    """Extract archetypal plot arcs from memory clusters."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    input_memory_set = models.ManyToManyField(SwarmMemoryEntry)
    archetype_tags = models.JSONField()
    codex_influence_map = models.JSONField()
    symbolic_plot_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class MemoryCompressionRitualTool(models.Model):
    """Compress multiple memories into a symbolic summary node."""

    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    source_entries = models.ManyToManyField(SwarmMemoryEntry)
    ritual_script = models.TextField()
    compressed_summary = models.TextField()
    aura_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CodexStoryReshaper(models.Model):
    """Restructure narrative timelines by codex rule or ritual reordering."""

    reshaper_title = models.CharField(max_length=150)
    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    target_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    belief_shift_map = models.JSONField()
    ritual_reorder_log = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


