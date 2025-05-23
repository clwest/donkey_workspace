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
