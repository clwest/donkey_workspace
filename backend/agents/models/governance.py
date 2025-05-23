from django.db import models

from .federation import CodexLinkedGuild
from .lore import SwarmCodex


class SymbolicConsensusChamber(models.Model):
    """Platform for deliberative codex evolution and belief tracking."""

    chamber_title = models.CharField(max_length=150)
    guilds_involved = models.ManyToManyField(CodexLinkedGuild)
    active_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    ritual_petitions = models.JSONField()
    belief_vote_matrix = models.JSONField()
    consensus_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.chamber_title


class RitualNegotiationEngine(models.Model):
    """Decision engine aligning codices through ritual interactions."""

    assistant_role_signatures = models.JSONField()
    codex_conflict_index = models.JSONField()
    ritual_interaction_logs = models.JSONField()
    proposed_ritual_fusion = models.JSONField(blank=True, null=True)
    codex_drift_score = models.FloatField(null=True, blank=True)
    resolution_vector_suggestions = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"NegotiationEngine {self.id}"


class NarrativeGovernanceModel(models.Model):
    """Assigns symbolic authority and cadence across the belief network."""

    governance_title = models.CharField(max_length=150)
    ruling_guild = models.ForeignKey(CodexLinkedGuild, on_delete=models.CASCADE)
    symbolic_policy = models.TextField()
    codex_weight_map = models.JSONField()
    ritual_rotation_sequence = models.JSONField()
    memory_impact_log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.governance_title
