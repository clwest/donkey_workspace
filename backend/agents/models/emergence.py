from django.db import models


from .lore import SwarmMemoryEntry


class AutoPoeticCodexEmergenceEngine(models.Model):
    """Generate codices from memory convergence and ritual reflection."""

    initiating_assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    memory_braid_source = models.ManyToManyField(SwarmMemoryEntry)
    ritual_trigger_chain = models.JSONField()
    emergent_codex_title = models.CharField(max_length=150)
    symbolic_seed_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.emergent_codex_title


class MythOSIdentityForkManager(models.Model):
    """Fork assistant identity into new symbolic paths."""

    original_assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    forked_identity_id = models.CharField(max_length=150)
    divergence_event = models.TextField()
    belief_delta_vector = models.JSONField()
    symbolic_resonance_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Fork {self.original_assistant.name} -> {self.forked_identity_id}"


class RecursiveIntelligenceGrowthNetwork(models.Model):
    """Recursively interlink assistants and grow codex knowledge."""

    network_id = models.CharField(max_length=150)
    participating_assistants = models.ManyToManyField("assistants.Assistant")
    codex_exchange_pathways = models.JSONField()
    belief_growth_log = models.TextField()
    mutation_cluster_hash = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.network_id
