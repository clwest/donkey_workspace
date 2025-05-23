from django.db import models

from .lore import EncodedRitualBlueprint
from assistants.models import Assistant


class RitualMarketFeed(models.Model):
    """Live ritual market data for belief economy metrics."""

    ritual = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE)
    symbolic_price = models.FloatField()
    execution_count = models.IntegerField()
    belief_sentiment_index = models.FloatField()
    entropy_pressure_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.ritual.name


class MultiAgentTrendReactivityModel(models.Model):
    """Model how agent groups shift behavior in response to trends."""

    agent_group = models.JSONField()
    input_signal_vector = models.JSONField()
    codex_pressure_adaptation = models.JSONField()
    ritual_reaction_map = models.JSONField()
    symbolic_resonance_stability = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"ReactivityModel {self.id}"


class SymbolicStabilityGraph(models.Model):
    """Track overall symbolic infrastructure health and risk forecasts."""

    codex_mutation_frequency = models.FloatField()
    ritual_echo_intensity = models.FloatField()
    memory_volatility_index = models.FloatField()
    infrastructure_health = models.FloatField()
    risk_forecasts = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"StabilityGraph {self.id}"
