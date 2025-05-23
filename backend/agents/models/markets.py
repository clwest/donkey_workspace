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


class CodexCurrencyModule(models.Model):
    """Assigns symbolic value to codex and ritual activities."""

    codex = models.ForeignKey('agents.SwarmCodex', on_delete=models.CASCADE)
    mutation_impact_score = models.FloatField()
    ritual_weight_multiplier = models.FloatField()
    symbolic_value_curve = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return str(self.codex)


class SymbolicInfluenceLedger(models.Model):
    """Tracks belief transactions and ritual scores for assistants."""

    user_id = models.CharField(max_length=150)
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    codex_transactions = models.JSONField()
    ritual_scores = models.JSONField()
    memory_contributions = models.ManyToManyField('agents.SwarmMemoryEntry')
    influence_balance = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return self.user_id


class BeliefContributionMarketplace(models.Model):
    """Federated exchange for codex proposals and ritual endorsements."""

    proposal_title = models.CharField(max_length=150)
    proposer = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    staked_tokens = models.JSONField()
    endorsed_rituals = models.JSONField()
    ranked_insights = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return self.proposal_title


class RitualIncentiveSystem(models.Model):
    """Reward engine issuing symbolic value for completed rituals."""

    ritual = models.ForeignKey(
        'agents.EncodedRitualBlueprint', on_delete=models.CASCADE
    )
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    user_id = models.CharField(max_length=150)
    symbolic_reward = models.FloatField()
    codex_tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return f"Reward {self.symbolic_reward}"


class SymbolicFundingProtocol(models.Model):
    """Manage symbolic value distribution across guild initiatives."""

    guild = models.ForeignKey(
        'assistants.CodexLinkedGuild', on_delete=models.CASCADE
    )
    symbolic_reserve = models.FloatField()
    proposed_allocations = models.JSONField()
    contributor_votes = models.JSONField()
    approved_projects = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):  # pragma: no cover - display helper
        return str(self.guild)
