from django.db import models

class BeliefCascadeGraph(models.Model):
    """Graph showing how a codex clause cascades through the swarm."""
    clause_id = models.CharField(max_length=200)
    graph_data = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]


class CascadeImpactNode(models.Model):
    graph = models.ForeignKey(BeliefCascadeGraph, on_delete=models.CASCADE, related_name="impact_nodes")
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    memory = models.ForeignKey("memory.MemoryEntry", null=True, blank=True, on_delete=models.SET_NULL)
    impact_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CascadeEffectTrace(models.Model):
    node = models.ForeignKey(CascadeImpactNode, on_delete=models.CASCADE, related_name="traces")
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class RoleTensionMetric(models.Model):
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE, related_name="tension_metrics")
    conflicting_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="conflicting_tension_metrics"
    )
    tension_score = models.FloatField(default=0.0)
    conflict_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AssistantArchetypeConflict(models.Model):
    description = models.TextField()
    assistants = models.ManyToManyField("assistants.Assistant")
    status = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CollisionResolutionProposal(models.Model):
    conflict = models.ForeignKey(AssistantArchetypeConflict, on_delete=models.CASCADE, related_name="proposals")
    proposed_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    proposal = models.TextField()
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class StabilizationCampaign(models.Model):
    title = models.CharField(max_length=150)
    target_clause_id = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CodexClauseVoteLog(models.Model):
    campaign = models.ForeignKey(StabilizationCampaign, on_delete=models.CASCADE, related_name="votes")
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    vote_choice = models.CharField(max_length=10)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CampaignSymbolicGainEstimate(models.Model):
    campaign = models.ForeignKey(StabilizationCampaign, on_delete=models.CASCADE, related_name="gain_estimates")
    estimated_gain = models.FloatField()
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class CodexClauseUpdateLog(models.Model):
    """Record of the clause text before and after a campaign."""

    campaign = models.ForeignKey(StabilizationCampaign, on_delete=models.CASCADE, related_name="updates")
    clause_before = models.TextField(blank=True)
    clause_after = models.TextField(blank=True)
    symbolic_gain = models.FloatField(default=0.0)
    symbolic_loss = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
