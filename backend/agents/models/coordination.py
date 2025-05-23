from django.db import models



class CollaborationThread(models.Model):
    """Symbolic container for cross-assistant collaboration."""

    title = models.CharField(max_length=150)
    participants = models.ManyToManyField("assistants.Assistant")
    narrative_focus = models.TextField()
    symbolic_tags = models.JSONField()
    originating_memory = models.ForeignKey(
        "agents.SwarmMemoryEntry", on_delete=models.SET_NULL, null=True
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DelegationStream(models.Model):
    """Intent-weighted task routing between assistants."""

    stream_name = models.CharField(max_length=100)
    source_assistant = models.ForeignKey(
        "assistants.Assistant", related_name="stream_source", on_delete=models.CASCADE
    )
    target_assistant = models.ForeignKey(
        "assistants.Assistant", related_name="stream_target", on_delete=models.CASCADE
    )
    symbolic_context = models.JSONField()
    task_rationale = models.TextField()
    stream_status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)


class MythflowInsight(models.Model):
    """Insight artifact guiding swarm narrative flow."""

    thread = models.ForeignKey(CollaborationThread, on_delete=models.CASCADE)
    generated_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    insight_summary = models.TextField()
    symbolic_shift_detected = models.BooleanField(default=False)
    recommended_action = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SymbolicCoordinationEngine(models.Model):
    """Role-aware coordination system driven by symbolic signals."""

    guild = models.ForeignKey("assistants.AssistantGuild", on_delete=models.CASCADE)
    active_signals = models.JSONField()
    coordination_strategy = models.TextField()
    tasks_assigned = models.JSONField()
    last_sync = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_sync"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"CoordEngine for {self.guild.name}"


class MythflowOrchestrationPlan(models.Model):
    """Symbolic narrative planning structure driven by mythflow."""

    title = models.CharField(max_length=150)
    lead_assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    goal_sequence = models.JSONField()
    narrative_constraints = models.TextField()
    participating_agents = models.ManyToManyField(
        "assistants.Assistant", related_name="mythflow_plans"
    )
    mythflow_state = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)


class DirectiveMemoryNode(models.Model):
    """Durable symbolic intent memory across cycles."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    purpose_statement = models.TextField()
    triggering_conditions = models.JSONField()
    directive_tags = models.JSONField()
    temporal_scope = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class SymbolicPlanningLattice(models.Model):
    """Symbolic graph of mythic continuity and purpose weighting."""

    associated_plan = models.ForeignKey(
        MythflowOrchestrationPlan, on_delete=models.CASCADE
    )
    role_nodes = models.JSONField()
    narrative_edges = models.JSONField()
    alignment_scores = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)
