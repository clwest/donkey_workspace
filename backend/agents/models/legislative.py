from django.db import models
from .federation import CodexLinkedGuild
from .lore import SwarmCodex


class CodexFederationArchitecture(models.Model):
    """Structure describing federated codex governance."""

    federation_name = models.CharField(max_length=150)
    member_codices = models.ManyToManyField(SwarmCodex, blank=True)
    alliance_map = models.JSONField(default=dict, blank=True)
    treaty_framework = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.federation_name


class SymbolicTreatyProtocol(models.Model):
    """Defines codex-aligned treaty clauses and enforcement terms."""

    treaty_name = models.CharField(max_length=150)
    codex_scope = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    clause_map = models.JSONField(default=dict, blank=True)
    enforcement_guidelines = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.treaty_name


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
