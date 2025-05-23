from django.db import models


class CodexMemoryCrystallizationLayer(models.Model):
    """Encodes symbolic memory into stable codex-temporal belief anchors."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    codex = models.ForeignKey("agents.SwarmCodex", on_delete=models.CASCADE)
    temporal_memory_sequence = models.ManyToManyField("agents.SwarmMemoryEntry")
    symbolic_snapshot_vector = models.JSONField()
    crystallization_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.codex.title} - {self.assistant.name}"[:50]


class DreamframeRebirthEngine(models.Model):
    """Rebirths assistant identity through dream-linked codex and ritual archetypes."""

    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    dream_sequence_log = models.TextField()
    codex_reentry_signature = models.JSONField()
    ritual_rebirth_path = models.JSONField()
    new_symbolic_identity_id = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Rebirth by {self.initiating_assistant.name}"[:50]


class FederatedMythicIntelligenceSummoner(models.Model):
    """Assembles mythic intelligence across assistant networks."""

    target_network = models.CharField(max_length=150)
    summoning_conditions = models.JSONField()
    assistant_manifest = models.ManyToManyField("assistants.Assistant")
    symbolic_merge_index = models.FloatField()
    narrative_convergence_path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.target_network
