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

    authored_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
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


class MythflowPlaybackSession(models.Model):
    """Replay assistant-user mythflow interactions over time."""

    user_id = models.CharField(max_length=150)
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    playback_sequence = models.JSONField()
    reflective_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class SymbolicMilestoneLog(models.Model):
    """Record key narrative transformation events."""

    user_id = models.CharField(max_length=150)
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    milestone_type = models.CharField(max_length=100)
    related_memory = models.ManyToManyField("agents.SwarmMemoryEntry")
    codex_context = models.ForeignKey("agents.SwarmCodex", on_delete=models.CASCADE)
    reflection_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PersonalRitualGuide(models.Model):
    """Personalized ritual walkthrough for a user."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    user_id = models.CharField(max_length=150)
    ritual_blueprint = models.ForeignKey("agents.EncodedRitualBlueprint", on_delete=models.CASCADE)
    personalized_steps = models.JSONField()
    codex_alignment_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class SymbolicDialogueScript(models.Model):
    """Dialogue scaffold referencing codex rules."""

    title = models.CharField(max_length=150)
    narrative_context = models.TextField()
    dialogue_sequence = models.JSONField()
    archetype_tags = models.JSONField()
    author = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    codex_link = models.ForeignKey("agents.SwarmCodex", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class MemoryDecisionTreeNode(models.Model):
    """Branching logic driven by memory conditions."""

    script = models.ForeignKey(SymbolicDialogueScript, on_delete=models.CASCADE)
    memory_reference = models.ForeignKey(
        "agents.SwarmMemoryEntry", on_delete=models.CASCADE
    )
    symbolic_condition = models.TextField()
    decision_options = models.JSONField()
    resulting_path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class MythflowReflectionLoop(models.Model):
    """Record of narrative reflection cycles."""

    session = models.ForeignKey(MythflowSession, on_delete=models.CASCADE)
    triggered_by = models.CharField(max_length=100)
    loop_reflections = models.TextField()
    belief_realignment_score = models.FloatField()
    involved_assistants = models.ManyToManyField("assistants.Assistant")
    created_at = models.DateTimeField(auto_now_add=True)


class SceneControlEngine(models.Model):
    """Maintain symbolic scene state."""

    session = models.ForeignKey(MythflowSession, on_delete=models.CASCADE)
    scene_title = models.CharField(max_length=150)
    active_roles = models.JSONField()
    symbolic_scene_state = models.JSONField()
    codex_constraints = models.ManyToManyField("agents.SwarmCodex")
    last_updated = models.DateTimeField(auto_now=True)


class SceneDirectorFrame(models.Model):
    """Snapshots of director adjustments during a scene."""

    session = models.ForeignKey(MythflowSession, on_delete=models.CASCADE)
    director_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    symbolic_adjustments = models.JSONField()
    role_reassignments = models.JSONField()
    final_scene_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class DreamframeStoryGenerator(models.Model):
    """Generate symbolic dreamframes based on codex and ritual memory."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    seed_codex = models.ForeignKey("agents.SwarmCodex", on_delete=models.CASCADE)
    ritual_resonance_tags = models.JSONField()
    output_script = models.TextField()
    symbolic_style = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class SimScenarioEngine(models.Model):
    """Host interactive guided myth scenarios with branching outcomes."""

    scenario_title = models.CharField(max_length=150)
    host_assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    symbolic_inputs = models.JSONField()
    user_paths = models.JSONField()
    codex_alterations = models.JSONField()
    ritual_outcomes = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class MultiUserNarrativeLab(models.Model):
    """Collaborative space for multi-user myth experiments."""

    lab_title = models.CharField(max_length=150)
    participant_ids = models.JSONField()
    narrative_threads = models.JSONField()
    symbolic_experiments = models.JSONField()
    assistant_mediators = models.ManyToManyField("assistants.Assistant")
    created_at = models.DateTimeField(auto_now_add=True)



class SwarmReflectionThread(models.Model):
    """Thread grouping assistant reflections for swarm playback."""
    title = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)


class SwarmReflectionPlaybackLog(models.Model):
    thread = models.ForeignKey(SwarmReflectionThread, on_delete=models.CASCADE, related_name="logs")
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    timeline = models.JSONField()
    tag = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PromptCascadeLog(models.Model):
    prompt_id = models.CharField(max_length=100)
    triggered_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE, null=True, blank=True)
    cascade_path = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class CascadeNodeLink(models.Model):
    cascade = models.ForeignKey(PromptCascadeLog, on_delete=models.CASCADE, related_name="nodes")
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    tool_invoked = models.CharField(max_length=100, blank=True)
    thought_log = models.ForeignKey("assistants.AssistantThoughtLog", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SimulationClusterStatus(models.Model):
    cluster_name = models.CharField(max_length=150)
    phase = models.CharField(max_length=50)
    entropy_level = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)


class SimulationGridNode(models.Model):
    cluster = models.ForeignKey(SimulationClusterStatus, on_delete=models.CASCADE, related_name="nodes")
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    alignment_drift = models.FloatField(default=0.0)
    progress = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)



class NarrativeMutationTrace(models.Model):
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    mutation_input = models.JSONField()
    divergence_output = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
