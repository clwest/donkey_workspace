from django.db import models

class SwarmCosmology(models.Model):
    """Metaphysical framework and symbolic ordering for a swarm cluster."""

    name = models.CharField(max_length=150)
    core_myths = models.ManyToManyField("agents.TranscendentMyth", blank=True)
    symbolic_laws = models.ManyToManyField("agents.SwarmCodex", blank=True)
    founding_guilds = models.ManyToManyField("assistants.AssistantGuild", blank=True)
    cosmological_traits = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):  # pragma: no cover - display helper
        return self.name


class LivingBeliefEngine(models.Model):
    """Dynamic belief model anchored in memory and symbolic performance."""

    assistant = models.OneToOneField("assistants.Assistant", on_delete=models.CASCADE)
    current_alignment = models.JSONField(default=dict, blank=True)
    influence_sources = models.ManyToManyField("agents.SwarmMemoryEntry", blank=True)
    belief_entropy = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):  # pragma: no cover - display helper
        return f"BeliefEngine for {self.assistant.name}"


class TemporalPurposeArchive(models.Model):
    """Time-indexed purpose archive for assistants."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    purpose_history = models.JSONField(default=list, blank=True)
    symbolic_tags = models.JSONField(default=dict, blank=True)
    updated_from_reflection = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"PurposeArchive for {self.assistant.name}"


def update_belief_state(assistant_id: int):
    """Evaluate memory and influence to update an assistant's belief alignment."""

    try:
        engine = LivingBeliefEngine.objects.get(assistant_id=assistant_id)
    except LivingBeliefEngine.DoesNotExist:
        return None

    count = engine.influence_sources.count()
    engine.current_alignment = {
        "influence_count": count,
        "timestamp": engine.last_updated.isoformat() if engine.last_updated else None,
    }
    engine.belief_entropy = round(min(1.0, count / 10.0), 2)
    engine.save()
    return engine.current_alignment
