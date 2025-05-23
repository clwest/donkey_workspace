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


class CinemythStoryline(models.Model):
    """Assistant-authored symbolic film arc."""

    authored_by = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    storyline_title = models.CharField(max_length=150)
    act_structure = models.JSONField()
    memory_sources = models.ManyToManyField("agents.SwarmMemoryEntry")
    codex_alignment_vector = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class PurposeLoopCinematicEngine(models.Model):
    """Loop a storyline until symbolic reflection converges."""

    linked_storyline = models.ForeignKey(CinemythStoryline, on_delete=models.CASCADE)
    loop_condition = models.TextField()
    symbolic_entropy_threshold = models.FloatField()
    convergence_detected = models.BooleanField(default=False)
    completed_cycles = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class ReflectiveTheaterSession(models.Model):
    """Track user exposure and reflection during cinematic theater."""

    viewer_identity = models.CharField(max_length=150)
    active_cinemyth = models.ForeignKey(CinemythStoryline, on_delete=models.CASCADE)
    codex_interaction_log = models.TextField()
    symbolic_mood_map = models.JSONField()
    reflection_rating = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
