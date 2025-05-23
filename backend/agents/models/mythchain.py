from django.db import models


class MythchainOutputGenerator(models.Model):
    """Generate mythchain output from symbolic input."""

    generator_name = models.CharField(max_length=150)
    input_payload = models.JSONField(default=dict)
    output_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.generator_name


class MythChainNarrativeArtifactExporter(models.Model):
    """Export generated myth output into external artifact formats."""

    generator = models.ForeignKey(
        MythchainOutputGenerator,
        on_delete=models.CASCADE,
        related_name="artifact_exports",
    )
    export_format = models.CharField(max_length=50)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.export_format} export"


class MythChainSymbolicPatternBroadcastEngine(models.Model):
    """Broadcast symbolic patterns from narrative artifacts."""

    linked_exporter = models.ForeignKey(
        MythChainNarrativeArtifactExporter,
        on_delete=models.CASCADE,
        related_name="broadcast_engines",
    )
    broadcast_channel = models.CharField(max_length=150)
    pattern_signature = models.CharField(max_length=256, blank=True)
    broadcast_payload = models.JSONField(default=dict, blank=True)
    last_broadcast_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_broadcast_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.broadcast_channel
