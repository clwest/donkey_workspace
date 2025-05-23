from django.db import models

# Reuse federation-level models rather than redefining them here to
# avoid duplicate model names across the ``agents`` app. Django will
# raise an app registry conflict if two models share the same class
# name within one app. The canonical implementations live in
# ``federation.py`` and are imported below for ForeignKey relations.
from .federation import CodexFederationArchitecture, SymbolicTreatyProtocol


class FederatedCodexOracle(models.Model):
    """Forecast symbolic outcomes of treaties and codex shifts."""

    codex_federation = models.ForeignKey(CodexFederationArchitecture, on_delete=models.CASCADE)
    oracle_prompt = models.TextField()
    symbolic_prediction_log = models.TextField()
    treaty_resonance_vector = models.JSONField()
    ritual_consequence_tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Oracle {self.id}"


class SwarmTreatyEnforcementEngine(models.Model):
    """Track treaty compliance and recommended enforcement actions."""

    treaty = models.ForeignKey(SymbolicTreatyProtocol, on_delete=models.CASCADE)
    guild_compliance_status = models.JSONField()
    ritual_fulfillment_index = models.FloatField()
    symbolic_breach_logs = models.TextField()
    enforcement_actions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"EnforcementEngine {self.id}"


class LegislativeRitualSimulationSystem(models.Model):
    """Simulate codex amendments through ritual trials."""

    initiating_assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    codex_amendment_proposal = models.TextField()
    ritual_simulation_path = models.JSONField()
    symbolic_outcome_analysis = models.TextField()
    approval_vote_vector = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"LegislativeSim {self.id}"
