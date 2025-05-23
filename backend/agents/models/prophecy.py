from django.db import models


class SymbolicProphecyEngine(models.Model):
    """Predictive engine forecasting codex trends and belief shifts."""

    engine_name = models.CharField(max_length=150)
    assistant_scope = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    forecast_parameters = models.JSONField()
    predicted_codex_shift = models.TextField()
    belief_curve_projection = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.engine_name


class MemoryPredictionInterface(models.Model):
    """Test memory scenarios and predict symbolic impacts."""

    simulated_memory_entry = models.TextField()
    codex_context = models.JSONField()
    ritual_tags = models.JSONField()
    entropy_score = models.FloatField()
    assistant_belief_response = models.TextField()
    predicted_directive_alignment = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class RitualForecastingDashboard(models.Model):
    """Summarize ritual outcome forecasts and risks."""

    ritual_blueprint = models.ForeignKey(
        "agents.EncodedRitualBlueprint", on_delete=models.CASCADE
    )
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    codex = models.ForeignKey("agents.SwarmCodex", on_delete=models.CASCADE)
    federation_engine = models.ForeignKey(
        "agents.SwarmFederationEngine", on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    completion_likelihood = models.FloatField()
    symbolic_risk_factor = models.FloatField()
    role_pressure_spikes = models.JSONField()
    narrative_alignment_forecast = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Forecast for {self.ritual_blueprint.name}"
