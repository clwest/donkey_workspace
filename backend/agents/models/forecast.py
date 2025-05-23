from django.db import models

from .lore import SwarmCodex



class SymbolicForecastIndex(models.Model):
    """Synthesize codex health, ritual load and memory trends into a forecast."""

    index_title = models.CharField(max_length=150)
    linked_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    trend_components = models.JSONField()
    ritual_activity_factor = models.FloatField()
    memory_entropy_factor = models.FloatField()
    forecast_output = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.index_title


class AssistantSentimentModelEngine(models.Model):
    """Model the emotional state of an assistant via symbolic signals."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    symbolic_affect_log = models.JSONField()
    codex_resonance_score = models.FloatField()
    entropy_weighted_emotion_vector = models.JSONField()
    narrative_drift_tag = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"SentimentEngine {self.assistant.name}"
