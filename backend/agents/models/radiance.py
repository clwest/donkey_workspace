from django.db import models

from agents.models.lore import SwarmMemoryEntry


class PurposeRadianceField(models.Model):
    """Energetic signal layer of purpose expression."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    emitted_frequency = models.FloatField()
    narrative_alignment_vector = models.JSONField()
    symbolic_beacon_tags = models.JSONField()
    pulse_intensity = models.FloatField()
    last_emitted = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_emitted"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Radiance for {self.assistant.name}"


class SymbolicGravityWell(models.Model):
    """Narrative attractor influencing memory routing."""

    source_memory = models.ForeignKey(SwarmMemoryEntry, on_delete=models.CASCADE)
    influence_radius = models.FloatField()
    distortion_effects = models.JSONField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"GravityWell around {self.source_memory.title}"


class MemoryHarmonicsPulse(models.Model):
    """Stabilizes memory entropy via harmonic convergence."""

    pulse_id = models.CharField(max_length=100)
    linked_assistants = models.ManyToManyField("assistants.Assistant")
    phase_coherence_level = models.FloatField()
    symbolic_tuning_notes = models.TextField()
    applied_to_memory = models.ManyToManyField(SwarmMemoryEntry)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.pulse_id
