from django.db import models


class PerformanceMetric(models.Model):
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class RitualPerformanceMetric(models.Model):
    """Tracks symbolic resonance and transformation alignment for ritual events."""

    ritual = models.ForeignKey(
        'agents.RitualArchiveEntry', on_delete=models.CASCADE
    )
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    symbolic_score = models.FloatField()
    transformation_alignment = models.FloatField()
    mythic_tags = models.JSONField()
    reflection_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class RitualReputationScore(models.Model):
    """Rating and reputation metrics for rituals."""

    ritual_name = models.CharField(max_length=150)
    symbolic_tags = models.JSONField(default=list)
    rating = models.FloatField()
    assistant_approval_ratio = models.FloatField()
    drift_reduction_effectiveness = models.FloatField()
    outcome_quality = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class CodexClauseVote(models.Model):
    """Vote record for codex clause mutations or forks."""

    clause_id = models.CharField(max_length=200)
    suggested_mutation = models.TextField()
    symbolic_tags = models.JSONField(default=list)
    vote_choice = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)


class SwarmAlignmentIndex(models.Model):
    """Real-time metric summarizing swarm alignment."""

    score = models.FloatField()
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class AssistantBeliefVector(models.Model):
    """Vector representation of an assistant's beliefs."""

    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE)
    vector = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class CodexClauseComplianceMap(models.Model):
    """Track clause compliance ratios across the swarm."""

    clause_id = models.CharField(max_length=200)
    compliance_ratio = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class TaskEvolutionSuggestion(models.Model):
    """Suggested improvement generated from clusters of task runs."""

    run_log = models.ForeignKey(
        'assistants.AssistantTaskRunLog', on_delete=models.CASCADE, related_name='evolution_suggestions'
    )
    suggestion_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PromptVersionTrace(models.Model):
    """Track prompt versions and feedback scores."""

    prompt = models.ForeignKey('prompts.Prompt', on_delete=models.CASCADE, related_name='version_traces')
    previous = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    feedback_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SwarmTaskCluster(models.Model):
    """Cluster of similar task runs for pattern mining."""

    name = models.CharField(max_length=150)
    tasks = models.ManyToManyField('assistants.AssistantTaskRunLog', related_name='task_clusters')
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
