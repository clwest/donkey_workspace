from django.db import models


class MythchainOutputGenerator(models.Model):
    """Encode dreams and memories into mythchain artifacts."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    seed_memory = models.ManyToManyField("agents.SwarmMemoryEntry")
    output_title = models.CharField(max_length=150)
    codex_alignment_map = models.JSONField()
    symbolic_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.output_title


class NarrativeArtifactExporter(models.Model):
    """Package story segments and ritual outputs for download."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    artifact_title = models.CharField(max_length=150)
    source_story = models.ForeignKey(
        "story.Story", null=True, blank=True, on_delete=models.SET_NULL
    )
    export_format = models.CharField(max_length=10)
    auto_compress = models.BooleanField(default=False)
    symbolic_footer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.artifact_title


class SymbolicPatternBroadcastEngine(models.Model):
    """Broadcast belief patterns across assistants."""

    broadcast_title = models.CharField(max_length=150)
    source_guild = models.ForeignKey("assistants.CodexLinkedGuild", on_delete=models.CASCADE)
    symbolic_payload = models.JSONField()
    belief_waveform_data = models.JSONField()
    target_assistants = models.ManyToManyField("assistants.Assistant")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.broadcast_title
