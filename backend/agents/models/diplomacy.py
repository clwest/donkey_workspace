from django.db import models
from .lore import SwarmCodex, EncodedRitualBlueprint
from .federation import CodexLinkedGuild


class AssistantDiplomacyInterface(models.Model):
    """Belief-aligned diplomatic proposals between assistants."""

    initiator = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="diplomacy_initiator",
    )
    target = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="diplomacy_target",
    )
    proposal_type = models.CharField(max_length=100)
    dialogue_log = models.TextField()
    diplomatic_outcome = models.TextField()
    symbolic_agreement_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.initiator.name} -> {self.target.name}"


class CodexConvergenceCeremony(models.Model):
    """Ritualized codex merging mechanism."""

    converging_codices = models.ManyToManyField(
        SwarmCodex, related_name="convergence_ceremonies"
    )
    ceremony_title = models.CharField(max_length=150)
    symbolic_thresholds = models.JSONField()
    ritual_chain = models.ManyToManyField(EncodedRitualBlueprint)
    merged_codex_output = models.ForeignKey(
        SwarmCodex,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ceremony_merged_outputs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.ceremony_title


class MythicArbitrationCouncil(models.Model):
    """Multi-guild resolution of codex mutation disputes."""

    council_title = models.CharField(max_length=150)
    member_guilds = models.ManyToManyField(CodexLinkedGuild)
    belief_dispute_summary = models.TextField()
    council_votes = models.JSONField()
    resolved_codex_adjustments = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.council_title
