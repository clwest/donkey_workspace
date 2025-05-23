from django.db import models

class EpistemicCurrent(models.Model):
    """Dream-bound knowledge flow connecting assistants."""

    source = models.ForeignKey(
        "assistants.Assistant",
        related_name="epistemic_outbound",
        on_delete=models.CASCADE,
    )
    targets = models.ManyToManyField(
        "assistants.Assistant", related_name="epistemic_inbound"
    )
    dream_channel = models.BooleanField(default=True)
    content_summary = models.TextField()
    symbolic_tags = models.JSONField()
    current_strength = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class FeedbackAnchorNode(models.Model):
    """Anchor reflective insights for the swarm."""

    linked_memory = models.ForeignKey(
        "agents.SwarmMemoryEntry", on_delete=models.CASCADE
    )
    assistants_reflected = models.ManyToManyField("assistants.Assistant")
    insight_yield = models.TextField()
    symbolic_shift_detected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class KnowledgeEcologyMap(models.Model):
    """Visual map of symbolic knowledge terrain."""

    scope = models.CharField(max_length=100)
    symbolic_regions = models.JSONField()
    active_currents = models.ManyToManyField(EpistemicCurrent)
    pressure_zones = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

