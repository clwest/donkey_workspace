from django.db import models


class NarrativeLightingEngine(models.Model):
    """Dynamic lighting state tied to codex tone and session mood."""

    codex = models.ForeignKey("agents.SwarmCodex", on_delete=models.CASCADE)
    memory_entry = models.ForeignKey(
        "agents.SwarmMemoryEntry", on_delete=models.SET_NULL, null=True, blank=True
    )
    mythflow_session = models.ForeignKey(
        "simulation.MythflowSession", on_delete=models.CASCADE
    )
    symbolic_trait = models.CharField(max_length=100, blank=True)
    background_pulse = models.CharField(max_length=100)
    lighting_tint = models.CharField(max_length=50)
    aura_particle_map = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Lighting for {self.codex.title}"


class CodexVisualElementLayer(models.Model):
    """Injects codex-defined symbolic assets into the UI."""

    codex = models.ForeignKey("agents.SwarmCodex", on_delete=models.CASCADE)
    borders = models.JSONField(default=dict, blank=True)
    glyph_overlays = models.JSONField(default=dict, blank=True)
    background_tone = models.CharField(max_length=50, blank=True)
    role_frame = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Visuals for {self.codex.title}"


class AssistantAestheticCloneProfile(models.Model):
    """Profile for cloning assistant visual traits."""

    source_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="clone_source",
        on_delete=models.CASCADE,
    )
    target_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="clone_target",
        on_delete=models.CASCADE,
    )
    traits_cloned = models.JSONField()
    symbolic_variants = models.JSONField()
    clone_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Clone {self.source_assistant} -> {self.target_assistant}"
