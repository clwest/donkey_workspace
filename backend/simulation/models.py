from django.db import models


class SimulationConfig(models.Model):
    name = models.CharField(max_length=150)
    assistant_ids = models.JSONField()
    scenario_description = models.TextField()
    parameters = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class SimulationRunLog(models.Model):
    config = models.ForeignKey(SimulationConfig, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    log_details = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class MythScenarioSimulator(models.Model):
    """Generates symbolic narrative simulations."""

    simulation_title = models.CharField(max_length=150)
    initiating_entity = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    selected_archetypes = models.JSONField()
    memory_inputs = models.ManyToManyField("agents.SwarmMemoryEntry")
    narrative_goals = models.TextField()
    simulation_outcome = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RitualInteractionEvent(models.Model):
    """Record of a ritual launched via the interface."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    ritual_blueprint = models.ForeignKey(
        "agents.RitualBlueprint", on_delete=models.CASCADE
    )
    trigger_method = models.CharField(max_length=100)
    reflection_notes = models.TextField(blank=True)
    memory_write_back = models.ForeignKey(
        "agents.SwarmMemoryEntry", on_delete=models.SET_NULL, null=True, blank=True
    )
    belief_impact_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)


class SimulationStateTracker(models.Model):
    """Tracks symbolic state across a simulation run."""

    simulator = models.ForeignKey(MythScenarioSimulator, on_delete=models.CASCADE)
    symbolic_state_snapshot = models.JSONField()
    role_drift_detected = models.BooleanField(default=False)
    codex_alignment_score = models.FloatField()
    memory_deltas = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class MythflowSession(models.Model):
    """Hosts a real-time symbolic interaction session."""

    session_name = models.CharField(max_length=150)
    active_scenario = models.ForeignKey(MythScenarioSimulator, on_delete=models.CASCADE)
    participants = models.ManyToManyField("assistants.Assistant")
    memory_trace = models.ManyToManyField("agents.SwarmMemoryEntry")
    live_codex_context = models.ManyToManyField("agents.SwarmCodex")
    session_status = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)


class SymbolicDialogueExchange(models.Model):
    """Records dialogue lines with symbolic context."""

    session = models.ForeignKey(MythflowSession, on_delete=models.CASCADE)
    sender = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    message_content = models.TextField()
    symbolic_intent = models.JSONField()
    codex_alignment_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class MemoryProjectionFrame(models.Model):
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    projected_memory_sequence = models.ManyToManyField("agents.SwarmMemoryEntry")
    symbolic_ritual_overlay = models.ForeignKey(
        "agents.EncodedRitualBlueprint", null=True, on_delete=models.SET_NULL
    )
    codex_context = models.ForeignKey(
        "agents.SwarmCodex", null=True, on_delete=models.SET_NULL
    )
    belief_trigger_tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class BeliefNarrativeWalkthrough(models.Model):
    walkthrough_title = models.CharField(max_length=150)
    guide_assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    decision_points = models.JSONField()
    symbolic_outcome_log = models.TextField()
    walkthrough_rating = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DreamframePlaybackSegment(models.Model):
    session_context = models.ForeignKey(MythflowSession, on_delete=models.CASCADE)
    playback_source = models.ForeignKey(MemoryProjectionFrame, on_delete=models.CASCADE)
    visual_style = models.CharField(max_length=100)
    narration_script = models.TextField()
    symbolic_affect_curve = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

