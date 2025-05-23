from django.db import models

from .lore import SwarmCodex, SwarmMemoryEntry


class SymbolicRoadmapPlan(models.Model):
    """Shared roadmap of symbolic transformation with narrative flow logic."""

    plan_title = models.CharField(max_length=150)
    contributors = models.JSONField()
    archetype_path = models.JSONField()
    ritual_checkpoints = models.JSONField()
    codex_constraints = models.ManyToManyField(SwarmCodex)
    memory_segments = models.ManyToManyField(SwarmMemoryEntry)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.plan_title


class CommunityMythPlanningArena(models.Model):
    """Public interface for proposing and refining collective symbolic story plans."""

    arena_title = models.CharField(max_length=150)
    participant_ids = models.JSONField()
    myth_proposals = models.JSONField()
    symbolic_tension_points = models.JSONField()
    codex_focus = models.ManyToManyField(SwarmCodex)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.arena_title


class FederatedCodexForecastTool(models.Model):
    """Predicts codex alignment and belief network shifts across the swarm."""

    forecast_title = models.CharField(max_length=150)
    codex_inputs = models.ManyToManyField(SwarmCodex)
    narrative_pressure_map = models.JSONField()
    projected_mutation_events = models.JSONField()
    convergence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.forecast_title
