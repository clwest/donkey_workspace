from django.db import models

from .lore import SwarmCodex


class CodexLinkedGuild(models.Model):
    """Symbolic collective anchored to a codex."""

    guild_name = models.CharField(max_length=150)
    anchor_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    member_assistants = models.ManyToManyField("assistants.Assistant")
    member_users = models.JSONField()
    ritual_focus = models.JSONField()
    codex_compliance_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.guild_name


class MythCommunityCluster(models.Model):
    """Informal community grouped by memory traits and archetypes."""

    cluster_name = models.CharField(max_length=150)
    trait_map = models.JSONField()
    collective_memory_tags = models.JSONField()
    participant_ids = models.JSONField()
    shared_archetype_signature = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.cluster_name


class SwarmFederationEngine(models.Model):
    """Coordinate guild actions and codex alignment across the swarm."""

    active_guilds = models.ManyToManyField(CodexLinkedGuild)
    symbolic_state_map = models.JSONField()
    federation_log = models.TextField()
    ritual_convergence_score = models.FloatField()
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_synced"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"FederationEngine {self.id}"
