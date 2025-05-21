from django.db import models
import uuid
from django.contrib.auth import get_user_model
from mcp_core.models import MemoryContext, Tag
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField


from django.utils import timezone


User = get_user_model()

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
        return f"{self.name} ({self.preferred_llm}, {self.execution_style})"


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
        if not self.season_tag:
            from .utils.swarm_temporal import get_season_marker

            date = self.created_at or timezone.now()
            self.season_tag = get_season_marker(date)
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
        return self.name


class MythDiplomacySession(models.Model):
    """Negotiation session between myth-based factions."""

    factions = models.ManyToManyField(
        "assistants.AssistantCouncil", related_name="myth_diplomacy_sessions"
    )
    topic = models.TextField()
    proposed_adjustments = models.TextField()
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


class AssistantCivilization(models.Model):
    """Cohesive society or faction formed by assistants."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    belief_system = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class LoreInheritanceLine(models.Model):
    """Track lore traits passed between entries across epochs."""

    source = models.ForeignKey(
        LoreEntry, on_delete=models.CASCADE, related_name="inherited_from"
    )
    descendant = models.ForeignKey(
        LoreEntry, on_delete=models.CASCADE, related_name="inherited_to"
    )
    traits_passed = models.JSONField()
    mutation_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.source} -> {self.descendant}"


class MythSimulationArena(models.Model):
    """Environment for myth-based civilization simulations."""

    name = models.CharField(max_length=150)
    participating_civilizations = models.ManyToManyField(AssistantCivilization)
    simulated_scenario = models.TextField()
    outcome_summary = models.TextField(blank=True)
    victory_vector = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name
