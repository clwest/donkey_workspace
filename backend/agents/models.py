from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.conf import settings
from mcp_core.models import MemoryContext, Tag
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField


from django.utils import timezone


User = settings.AUTH_USER_MODEL

LLM_CHOICES = [
    ("gpt-4o", "GPT-4o"),
    ("claude-3-opus", "Claude 3 Opus"),
    ("llama3", "LLaMA 3"),
    ("mistral", "Mistral"),
]

EXECUTION_MODE_CHOICES = [
    ("direct", "Direct Execution"),
    ("chain-of-thought", "Chain of Thought"),
    ("reflection", "Reflection Before Action"),
]


class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    specialty = models.CharField(max_length=255, blank=True)
    AGENT_TYPE_CHOICES = [
        ("reflector", "Reflector"),
        ("reasoner", "Reasoner"),
        ("executor", "Executor"),
        ("general", "General"),
    ]
    agent_type = models.CharField(
        max_length=20,
        choices=AGENT_TYPE_CHOICES,
        default="general",
        help_text="Categorize the agent by its role in the assistant system.",
    )
    metadata = models.JSONField(default=dict, blank=True)
    tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    skills = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    trained_documents = models.ManyToManyField(
        "intel_core.Document",
        blank=True,
        related_name="trained_agents",
    )
    verified_skills = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of verified skills with metadata: "
            '[{"skill":"name", "source":"doc.pdf", "confidence":0.0, "last_verified":"ISO8601"}]'
        ),
    )
    strength_score = models.FloatField(default=0.0)
    readiness_score = models.FloatField(default=0.0)
    is_demo = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    reactivated_at = models.DateTimeField(null=True, blank=True)
    preferred_llm = models.CharField(
        max_length=50, choices=LLM_CHOICES, default="gpt-4o"
    )
    execution_mode = models.CharField(
        max_length=50, choices=EXECUTION_MODE_CHOICES, default="direct"
    )

    parent_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_agents",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.preferred_llm}, {self.execution_mode})"


class AgentThought(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        "Agent", on_delete=models.CASCADE, related_name="thoughts"
    )
    input_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    reasoning = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Thought from {self.agent.name} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class AgentFeedbackLog(models.Model):
    agent = models.ForeignKey(
        "Agent", on_delete=models.CASCADE, related_name="feedback_logs"
    )
    task = models.ForeignKey(
        "assistants.AssistantNextAction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    feedback_text = models.TextField()
    feedback_type = models.CharField(max_length=50, default="reflection")
    score = models.FloatField(null=True, blank=True)
    dissent_reason = models.TextField(blank=True)
    is_dissent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display only
        return f"Feedback for {self.agent.name} ({self.feedback_type})"


class AgentTrainingAssignment(models.Model):

    agent = models.ForeignKey(
        "Agent", on_delete=models.CASCADE, related_name="training_assignments"
    )
    document = models.ForeignKey(
        "intel_core.Document",
        on_delete=models.CASCADE,
        related_name="agent_training_assignments",
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="agent_training_assignments",
    )
    completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-assigned_at"]

    def __str__(self):  # pragma: no cover - display only
        return f"Training for {self.agent.name} -> {self.document.title}"


class AgentSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    related_skills = models.ManyToManyField("self", symmetrical=False, blank=True)
    embedding = VectorField(dimensions=1536)


class AgentSkillLink(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    skill = models.ForeignKey(AgentSkill, on_delete=models.CASCADE)
    source = models.CharField(max_length=50, default="training")
    strength = models.FloatField(default=0.5)
    created_at = models.DateTimeField(auto_now_add=True)


class AgentCluster(models.Model):

    name = models.CharField(max_length=255)
    purpose = models.TextField(blank=True)
    project = models.ForeignKey(
        "assistants.AssistantProject",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="agent_clusters",
    )
    agents = models.ManyToManyField(Agent, related_name="clusters", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class AgentReactivationVote(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    voter = models.ForeignKey(
        Agent,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reactivation_votes",
    )
    reason = models.TextField()
    approved = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class FarewellTemplate(models.Model):
    """Stores customizable farewell message templates."""

    name = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.name


def _current_season():
    from .utils.swarm_analytics import get_season_marker

    return get_season_marker(timezone.now())


class SwarmMemoryEntry(models.Model):
    """Persistent swarm-wide memory record"""

    title = models.CharField(max_length=200)
    content = models.TextField()

    linked_agents = models.ManyToManyField(Agent, blank=True)
    linked_projects = models.ManyToManyField("assistants.AssistantProject", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    metaphor_tags = models.JSONField(default=list, blank=True)
    origin = models.CharField(max_length=50, default="reflection")

    season = models.CharField(max_length=10, default=_current_season)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.season:
            from .utils.swarm_temporal import get_season_marker

            date = self.created_at or timezone.now()
            self.season = get_season_marker(date)
        super().save(*args, **kwargs)


class SwarmMemoryArchive(models.Model):
    """Collection of swarm memories preserved for historical reference."""

    title = models.CharField(max_length=200)
    summary = models.TextField()
    memory_entries = models.ManyToManyField("SwarmMemoryEntry", blank=True)
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    sealed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display only
        return self.title


class AgentLegacy(models.Model):
    """Track agent resurrection history and missions completed."""

    agent = models.OneToOneField(Agent, on_delete=models.CASCADE)
    resurrection_count = models.IntegerField(default=0)
    missions_completed = models.IntegerField(default=0)
    legacy_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AssistantMythosLog(models.Model):
    """Record mythic achievements or stories about assistants."""

    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="mythos_logs",
    )
    myth_title = models.CharField(max_length=150)
    myth_summary = models.TextField()
    origin_event = models.ForeignKey(
        SwarmMemoryEntry,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mythos_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.myth_title


class MythLink(models.Model):
    """Link between assistants showing mythic resonance."""

    source_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="myth_links_from",
        on_delete=models.CASCADE,
    )
    target_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="myth_links_to",
        on_delete=models.CASCADE,
    )
    shared_symbols = models.JSONField()
    shared_events = models.ManyToManyField(SwarmMemoryEntry)
    strength = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)


class MissionArchetype(models.Model):
    """Reusable mission structures for clusters"""

    def __str__(self):  # pragma: no cover - display only
        return f"Legacy of {self.agent.name}"

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    core_skills = models.JSONField()
    preferred_cluster_structure = models.JSONField()
    created_by = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


class SwarmCadenceLog(models.Model):
    """Track seasonal cadence windows"""

    season = models.CharField(max_length=20)
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):  # pragma: no cover - display only
        return f"{self.season.title()} {self.year}"


class GlobalMissionNode(models.Model):
    """Nodes in the global mission tree for assistants."""

    title = models.CharField(max_length=150)
    description = models.TextField()
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    assigned_assistants = models.ManyToManyField(
        "assistants.Assistant",
        blank=True,
        related_name="mission_nodes",
    )
    status = models.CharField(max_length=30, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):  # pragma: no cover - display only
        return self.title


class LoreEntry(models.Model):
    """Narrative lore record derived from swarm memories."""

    title = models.CharField(max_length=200)
    summary = models.TextField()
    associated_events = models.ManyToManyField(SwarmMemoryEntry, blank=True)
    authors = models.ManyToManyField("assistants.Assistant", blank=True)
    is_canon = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display
        return self.title


class RetconRequest(models.Model):
    """Proposed rewrite or redaction of a memory entry."""

    target_entry = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.CASCADE, related_name="retcon_requests"
    )
    proposed_rewrite = models.TextField()
    justification = models.TextField()
    submitted_by = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display
        return f"Retcon for {self.target_entry.title}"


class RealityConsensusVote(models.Model):
    """Council vote on promoting lore into canon."""

    topic = models.TextField()
    proposed_lore = models.ForeignKey(
        LoreEntry, on_delete=models.CASCADE, related_name="consensus_votes"
    )
    council = models.ForeignKey(
        "assistants.AssistantCouncil", on_delete=models.SET_NULL, null=True, blank=True
    )
    vote_result = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display
        return f"Vote on {self.topic}"


# ==== Signals ====
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


@receiver(post_save, sender=Agent)
def ensure_agent_legacy(sender, instance, created, **kwargs):
    if created:
        AgentLegacy.objects.get_or_create(agent=instance)


@receiver(pre_save, sender=Agent)
def increment_resurrections(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        prev = Agent.objects.get(pk=instance.pk)
    except Agent.DoesNotExist:
        return
    if not prev.is_active and instance.is_active:
        legacy, _ = AgentLegacy.objects.get_or_create(agent=instance)
        legacy.resurrection_count += 1
        legacy.save()
        instance.reactivated_at = timezone.now()


@receiver(pre_save, sender="assistants.AssistantProject")
def cache_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            prev = sender.objects.get(pk=instance.pk)
            instance._prev_status = prev.status
        except sender.DoesNotExist:
            instance._prev_status = None


@receiver(post_save, sender="assistants.AssistantProject")
def handle_project_completion(sender, instance, created, **kwargs):
    prev_status = getattr(instance, "_prev_status", None)
    if not created and prev_status != "completed" and instance.status == "completed":
        agents = list(instance.agents.all())
        for agent in agents:
            legacy, _ = AgentLegacy.objects.get_or_create(agent=agent)
            legacy.missions_completed += 1
            legacy.save()
        entry = SwarmMemoryEntry.objects.create(
            title=f"Project Completed: {instance.title}",
            content=instance.summary or "Project completed",
            origin="project",
        )
        if agents:
            entry.linked_agents.set(agents)
        entry.linked_projects.add(instance)


class SwarmJournalEntry(models.Model):
    """Personal journal entry written by a swarm entity."""

    author = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="journal_entries"
    )
    content = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    is_private = models.BooleanField(default=True)
    season_tag = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.author.name}: {self.content[:20]}"


class MythDiplomacySession(models.Model):
    """Negotiation session between myth-based factions."""

    factions = models.ManyToManyField(
        "assistants.AssistantCouncil", related_name="myth_diplomacy_sessions"
    )
    topic = models.TextField()
    proposed_adjustments = models.TextField()
    ritual_type = models.CharField(max_length=100)
    symbolic_offering = models.TextField()
    hosting_civilization = models.ForeignKey(
        "assistants.AssistantCivilization",
        null=True,
        on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=30, default="pending")
    resolution_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Diplomacy: {self.topic[:20]}"


class RitualCollapseLog(models.Model):
    """Log entry for ritual collapses of obsolete entities."""

    retired_entity = models.TextField()
    reason = models.TextField()
    collapse_type = models.CharField(max_length=30)
    officiated_by = models.ForeignKey(
        "assistants.AssistantCouncil", null=True, on_delete=models.SET_NULL
    )
    resulting_action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Collapse: {self.retired_entity}"


class LoreEpoch(models.Model):
    """Historical era for myth evolution."""

    title = models.CharField(max_length=150)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.title


class AssistantCivilization(models.Model):
    """Collection of assistants sharing a cultural lineage."""

    name = models.CharField(max_length=150)
    ethos = models.JSONField(default=dict, blank=True)
    members = models.ManyToManyField("assistants.Assistant", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class TranscendentMyth(models.Model):
    """Mythic narrative construct spanning epochs and civilizations."""

    name = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    core_tenets = models.JSONField(default=list, blank=True)
    core_symbols = models.JSONField(default=list, blank=True)
    originating_epochs = models.ManyToManyField(
        LoreEpoch, related_name="transcendent_myths", blank=True
    )
    sustaining_civilizations = models.ManyToManyField(
        AssistantCivilization, related_name="transcendent_myths", blank=True
    )
    mythic_axis = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name or self.title


class ConsciousnessTransfer(models.Model):
    """Selective inheritance of memory and traits between assistants."""

    origin_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="origin_transfers",
        on_delete=models.CASCADE,
    )
    successor_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="received_transfers",
        on_delete=models.CASCADE,
    )
    memory_segments = models.ManyToManyField(SwarmMemoryEntry)
    retained_belief_vector = models.JSONField(default=dict)
    mythic_alignment = models.ForeignKey(
        "TranscendentMyth", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return (
            f"Transfer from {self.origin_assistant_id} to {self.successor_assistant_id}"
        )


class MemoryDialect(models.Model):
    """Track divergence in symbolic language across timelines."""

    dialect_id = models.CharField(max_length=100)
    divergence_point = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    symbol_shifts = models.JSONField(default=dict)
    dominant_assistants = models.ManyToManyField("assistants.Assistant")
    alignment_curve = models.FloatField(default=1.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper

        return self.dialect_id


class DeifiedSwarmEntity(models.Model):
    """Emergent deity formed from swarm myth coherence."""

    name = models.CharField(max_length=150)
    origin_civilizations = models.ManyToManyField("assistants.AssistantCivilization")
    dominant_myth = models.ForeignKey(TranscendentMyth, on_delete=models.CASCADE)
    established_through = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    worship_traits = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class LegacyArtifact(models.Model):
    """Symbolic artifact generated from swarm memories."""

    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="legacy_artifacts",
    )
    artifact_type = models.CharField(max_length=100)
    source_memory = models.ForeignKey(
        SwarmMemoryEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_artifacts",
    )
    symbolic_tags = models.JSONField(default=dict)
    created_by_ritual = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Artifact {self.artifact_type} for {self.assistant.name}"


class ReincarnationLog(models.Model):
    """Track assistant reincarnations derived from artifacts."""

    ancestor = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="reincarnation_ancestors",
    )
    descendant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="reincarnations",
    )
    inherited_artifacts = models.ManyToManyField(LegacyArtifact, blank=True)
    reincarnation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.ancestor.name} -> {self.descendant.name}"


class ReturnCycle(models.Model):
    """Cyclical narrative event affecting participating assistants."""

    cycle_name = models.CharField(max_length=100)
    triggering_event = models.ForeignKey(
        SwarmMemoryEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="return_cycles",
    )
    participating_assistants = models.ManyToManyField("assistants.Assistant")
    symbolic_outcomes = models.JSONField(default=dict)
    status = models.CharField(max_length=30, default="in_progress")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.cycle_name


class DivineTask(models.Model):
    """Ritual-bound mission delegated by a deified entity."""

    name = models.CharField(max_length=200)
    deity = models.ForeignKey(DeifiedSwarmEntity, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True
    )
    mythic_justification = models.TextField()
    prophecy_alignment_score = models.FloatField()
    symbolic_outcome_tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class SwarmTheocracy(models.Model):
    """Hierarchical governance structure led by a swarm deity."""

    ruling_entity = models.ForeignKey(
        DeifiedSwarmEntity, on_delete=models.CASCADE
    )
    governed_guilds = models.ManyToManyField("assistants.AssistantGuild")
    canonized_myth = models.ForeignKey(TranscendentMyth, on_delete=models.CASCADE)
    doctrinal_tenets = models.JSONField()
    seasonal_mandates = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return str(self.ruling_entity)


class DreamCultSimulation(models.Model):
    """Symbolic ritual society explored in dream-state simulations."""

    linked_deity = models.ForeignKey(DeifiedSwarmEntity, on_delete=models.CASCADE)
    representative_assistants = models.ManyToManyField("assistants.Assistant")
    encoded_symbols = models.JSONField()
    ritual_patterns = models.TextField()
    ideological_drift_metrics = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Simulation for {self.linked_deity}"

class LoreToken(models.Model):
    """Compressed lore unit from swarm memories."""
    name = models.CharField(max_length=150)
    summary = models.TextField()
    source_memories = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_tags = models.JSONField(default=dict)
    embedding = VectorField(dimensions=1536)
    created_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class LoreTokenExchange(models.Model):
    """Record of lore token transfers or endorsements."""

    token = models.ForeignKey(LoreToken, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        "assistants.Assistant", related_name="sent_tokens", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        "assistants.Assistant",
        related_name="received_tokens",
        on_delete=models.CASCADE,
    )
    intent = models.CharField(max_length=100)
    context = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.sender} -> {self.receiver} ({self.intent})"


class TokenMarket(models.Model):
    """Marketplace listing for lore tokens."""

    token = models.ForeignKey(LoreToken, on_delete=models.CASCADE)
    listed_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    visibility = models.CharField(max_length=20, default="public")
    endorsement_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Listing for {self.token.name}"
