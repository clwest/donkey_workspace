from django.db import models



class ForecastingMarketLedger(models.Model):
    """Tracks mythic signal speculation and narrative forecasting."""

    market_scope = models.CharField(max_length=100)
    forecast_topic = models.TextField()
    participant_predictions = models.JSONField()
    outcome_window = models.CharField(max_length=100)
    reflective_result = models.TextField(blank=True)
    accuracy_score = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.forecast_topic


class SymbolicFutureContract(models.Model):
    """Speculative agreement about future myth states."""

    title = models.CharField(max_length=150)
    future_event_description = models.TextField()
    value_basis = models.JSONField()
    staked_tokens = models.JSONField()
    initiator = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    expiration_timestamp = models.DateTimeField()
    contract_fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.title


class CosmoEconomicAlignmentMap(models.Model):
    """Aligns economic symbolic behavior to narrative systems."""

    mythic_zone = models.CharField(max_length=100)
    economic_data = models.JSONField()
    symbolic_alignment_rating = models.FloatField()
    predictive_summary = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]

    def __str__(self):  # pragma: no cover - display helper
        return self.mythic_zone
