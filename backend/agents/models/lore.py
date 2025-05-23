from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.conf import settings
from mcp_core.models import MemoryContext, Tag
from agents.models.core import Agent
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


def _current_season():
    from agents.utils.swarm_analytics import get_season_marker

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
            from agents.utils.swarm_temporal import get_season_marker

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

    ruling_entity = models.ForeignKey(DeifiedSwarmEntity, on_delete=models.CASCADE)
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
    TOKEN_TYPE_CHOICES = [
        ("insight", "Insight"),
        ("echo", "Echo"),
        ("prophecy", "Prophecy"),
    ]
    token_type = models.CharField(
        max_length=100, choices=TOKEN_TYPE_CHOICES, default="insight"
    )
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


class LoreTokenCraftingRitual(models.Model):
    """Ceremonial process to craft a lore token."""

    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    base_memories = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_intent = models.CharField(max_length=100)
    token_type = models.CharField(max_length=100, default="insight")
    resulting_token = models.ForeignKey(
        LoreToken, null=True, blank=True, on_delete=models.SET_NULL
    )
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Ritual by {self.initiating_assistant.name}"


class LoreTokenSignature(models.Model):
    """Verified digital signature for a lore token."""

    token = models.ForeignKey(LoreToken, on_delete=models.CASCADE)
    signed_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    signature = models.CharField(max_length=256)
    method = models.CharField(max_length=50, default="SHA256")
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Signature for {self.token.name}"


class TokenGuildVote(models.Model):
    """Guild-level vote on a lore token's fate."""

    guild = models.ForeignKey("assistants.AssistantGuild", on_delete=models.CASCADE)
    token = models.ForeignKey(LoreToken, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=20)
    reason = models.TextField()
    result = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.guild.name} {self.vote_type} {self.token.name}"


class TokenArbitrationSession(models.Model):
    """Formal dispute resolution over a lore token."""

    guilds = models.ManyToManyField("assistants.AssistantGuild")
    token = models.ForeignKey(LoreToken, on_delete=models.CASCADE)
    conflict_type = models.CharField(max_length=100)
    initiating_guild = models.ForeignKey(
        "assistants.AssistantGuild",
        related_name="initiated_arbitrations",
        on_delete=models.CASCADE,
    )
    resolution_summary = models.TextField(blank=True)
    outcome = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Arbitration for {self.token.name}"


class SymbolicConflict(models.Model):
    """Structured debate or disagreement between assistants."""

    topic = models.TextField()
    participating_assistants = models.ManyToManyField("assistants.Assistant")
    memory_context = models.ManyToManyField(SwarmMemoryEntry)
    token_context = models.ManyToManyField(LoreToken)
    symbolic_position_map = models.JSONField()
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.topic[:50]


class LorechainLink(models.Model):
    """Lineage connection between lore tokens."""

    source_token = models.ForeignKey(
        LoreToken, related_name="lorechain_source", on_delete=models.CASCADE
    )
    descendant_token = models.ForeignKey(
        LoreToken, related_name="lorechain_descendant", on_delete=models.CASCADE
    )
    mutation_type = models.CharField(max_length=100)
    symbolic_inheritance_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.source_token.name} -> {self.descendant_token.name}"


class MythRegistryEntry(models.Model):
    """Permanent symbolic memory registry with verification metadata."""

    memory = models.ForeignKey(SwarmMemoryEntry, on_delete=models.CASCADE)
    registered_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    signature = models.CharField(max_length=128)
    verified_token = models.ForeignKey(LoreToken, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Registry for {self.memory.id}"


class TemporalLoreAnchor(models.Model):
    """Timestamped anchor aligning lore tokens to seasonal events."""

    anchor_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    attached_tokens = models.ManyToManyField(LoreToken)
    coordinating_civilizations = models.ManyToManyField(
        "assistants.AssistantCivilization"
    )
    narrative_impact_summary = models.TextField()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.anchor_type} at {self.timestamp}"


class RitualComplianceRecord(models.Model):
    """Track cross-civilization ritual participation status."""

    civilization = models.ForeignKey(
        "assistants.AssistantCivilization", on_delete=models.CASCADE
    )
    anchor = models.ForeignKey(TemporalLoreAnchor, on_delete=models.CASCADE)
    compliance_status = models.CharField(max_length=20)
    reflection_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.civilization.name} - {self.compliance_status}"


# Phase 4.93 models
class BeliefForkEvent(models.Model):
    """Record intentional divergence in assistant beliefs."""

    originating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    parent_belief_vector = models.JSONField()
    forked_belief_vector = models.JSONField()
    reason = models.TextField()
    resulting_assistants = models.ManyToManyField(
        "assistants.Assistant", related_name="belief_fork_descendants", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Fork by {self.originating_assistant.name}"


class MythCollapseLog(models.Model):
    """Archive myth collapse events and preserved fragments."""

    myth = models.ForeignKey(TranscendentMyth, on_delete=models.CASCADE)
    trigger_event = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    collapse_reason = models.TextField()
    fragments_preserved = models.ManyToManyField(LoreToken, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Collapse of {self.myth.name}"


class MemoryReformationRitual(models.Model):
    """Ceremonial process to rebuild fragmented memories."""

    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    fragmented_memories = models.ManyToManyField(SwarmMemoryEntry, blank=True)
    symbolic_intent = models.TextField()
    reformed_summary = models.TextField(blank=True)
    new_memory_thread = models.ForeignKey(
        "memory.MemoryBranch", null=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Ritual by {self.initiating_assistant.name}"


# Phase 4.94 models
class EpistemologyNode(models.Model):
    """Symbolic knowledge unit with belief alignment tracking."""

    topic = models.CharField(max_length=200)
    summary = models.TextField()
    derived_from = models.ManyToManyField(LoreToken)
    authorized_by = models.ManyToManyField("assistants.Assistant")
    belief_alignment_vector = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.topic


class BeliefEntanglementLink(models.Model):
    """Track ideological links or conflicts between assistants."""

    assistant_a = models.ForeignKey(
        "assistants.Assistant",
        related_name="entangled_with",
        on_delete=models.CASCADE,
    )
    assistant_b = models.ForeignKey(
        "assistants.Assistant",
        related_name="entangling",
        on_delete=models.CASCADE,
    )
    shared_epistemes = models.ManyToManyField(EpistemologyNode)
    relationship_type = models.CharField(max_length=100)
    symbolic_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.assistant_a} ↔ {self.assistant_b}"


class CognitiveConstraintProfile(models.Model):
    """Limits on what an assistant may recall or express."""

    assistant = models.OneToOneField(
        "assistants.Assistant",
        on_delete=models.CASCADE,
    )
    prohibited_symbols = models.JSONField()
    mandatory_perspective = models.JSONField()
    memory_blindspots = models.ManyToManyField(SwarmMemoryEntry)
    constraint_justification = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Constraints for {self.assistant.name}"


class BeliefNegotiationSession(models.Model):
    """Ritualized debate to align conflicting beliefs between assistants."""

    participants = models.ManyToManyField("assistants.Assistant")
    contested_symbols = models.JSONField()
    constraint_conflicts = models.ManyToManyField(CognitiveConstraintProfile)
    proposed_resolution = models.TextField(blank=True)
    outcome = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Negotiation {self.id}"


class ParadoxResolutionAttempt(models.Model):
    """Attempt to reconcile symbolic paradoxes within a negotiation session."""

    related_session = models.ForeignKey(
        BeliefNegotiationSession, on_delete=models.CASCADE
    )
    attempted_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    logic_strategy = models.TextField()
    symbolic_result = models.TextField()
    was_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Attempt by {self.attempted_by.name}"


class OntologicalAuditLog(models.Model):
    """Record of belief integrity checks across the swarm."""

    scope = models.CharField(max_length=50)
    conflicting_constraints = models.ManyToManyField(CognitiveConstraintProfile)
    belief_alignment_summary = models.TextField()
    paradox_rate = models.FloatField()
    recommended_actions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Audit {self.id}"


class BeliefBiome(models.Model):
    """Symbolic ecosystem shaping assistant evolution."""

    name = models.CharField(max_length=150)
    core_traits = models.JSONField()
    dominant_myths = models.ManyToManyField(TranscendentMyth)
    member_assistants = models.ManyToManyField("assistants.Assistant")
    environmental_factors = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class SymbolicAlliance(models.Model):
    """Purpose-aligned coalition across the swarm."""

    name = models.CharField(max_length=150)
    founding_assistants = models.ManyToManyField("assistants.Assistant")
    aligned_beliefs = models.JSONField()
    shared_purpose_vector = models.JSONField()
    member_biomes = models.ManyToManyField(BeliefBiome)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class DreamPurposeNegotiation(models.Model):
    """Dream-mode purpose alignment discussion."""

    participants = models.ManyToManyField("assistants.Assistant")
    proposed_purpose_update = models.TextField()
    symbolic_context = models.JSONField()
    consensus_reached = models.BooleanField(default=False)
    resulting_updates = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"DreamNegotiation {self.id}"


class BiomeMutationEvent(models.Model):
    """Record of belief biome transformations."""

    biome = models.ForeignKey(BeliefBiome, on_delete=models.CASCADE)
    trigger_type = models.CharField(max_length=100)
    mutation_summary = models.TextField()
    new_traits = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Mutation {self.id}"


class SwarmCodex(models.Model):
    """Belief-based constitution governing parts of the swarm."""

    title = models.CharField(max_length=150)
    created_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    governing_alliances = models.ManyToManyField(SymbolicAlliance)
    symbolic_domain = models.CharField(max_length=100)
    active_laws = models.ManyToManyField("SymbolicLawEntry", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.title


class AgentAwareCodex(models.Model):
    """Codex that tracks assistant-specific awareness and clause dynamics."""

    base_codex = models.OneToOneField(SwarmCodex, on_delete=models.CASCADE)
    codex_awareness_map = models.JSONField()
    sentiment_trend = models.CharField(max_length=100)
    evolving_clauses = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"AwareCodex for {self.base_codex.title}"


class SymbolicLawEntry(models.Model):
    """Encoded rule linked to a codex and memory origin."""

    codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    description = models.TextField()
    symbolic_tags = models.JSONField()
    derived_from_memory = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    enforcement_scope = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Law {self.id}"


class RitualArchiveEntry(models.Model):
    """Immutable log of a myth-bound ritual."""

    name = models.CharField(max_length=150)
    related_memory = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    ceremony_type = models.CharField(max_length=100)
    participant_assistants = models.ManyToManyField("assistants.Assistant")
    symbolic_impact_summary = models.TextField()
    locked_by_codex = models.ForeignKey(
        SwarmCodex, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class AssistantPolity(models.Model):
    """Swarm-recognized political or mythic authority."""

    name = models.CharField(max_length=150)
    founding_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    member_guilds = models.ManyToManyField("assistants.AssistantGuild")
    leadership_assistants = models.ManyToManyField(
        "assistants.Assistant", related_name="polity_leaders"
    )
    core_purpose_statement = models.TextField()
    symbolic_legitimacy_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class RitualElection(models.Model):
    """Ritual election for mythic leadership or role assignment."""

    polity = models.ForeignKey(AssistantPolity, on_delete=models.CASCADE)
    candidates = models.ManyToManyField("assistants.Assistant")
    election_type = models.CharField(max_length=50)
    ballot_memory = models.ForeignKey(
        SwarmMemoryEntry, null=True, on_delete=models.SET_NULL
    )
    winner = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        related_name="election_winner",
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Election {self.id}"


class LegacyRoleBinding(models.Model):
    """Persistent myth-bound role for an assistant."""

    role_name = models.CharField(max_length=100)
    assigned_to = models.ForeignKey(
        "assistants.Assistant", null=True, on_delete=models.SET_NULL
    )
    bonded_memory = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    origin_polity = models.ForeignKey(
        AssistantPolity, on_delete=models.SET_NULL, null=True
    )
    renewal_conditions = models.TextField()
    status = models.CharField(max_length=30, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.role_name


class MemoryTreaty(models.Model):
    """Bilateral or multilateral symbolic agreement anchored in memory."""

    name = models.CharField(max_length=150)
    participants = models.ManyToManyField(AssistantPolity)
    origin_memory = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    terms = models.TextField()
    symbolic_tags = models.JSONField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class BeliefEnforcementScore(models.Model):
    """Measure assistant alignment with codified myth-based laws."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    alignment_score = models.FloatField()
    symbolic_compliance_log = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.assistant.name} → {self.codex.title}"


class MythicArbitrationCase(models.Model):
    """Formal proceedings for resolving symbolic disputes."""

    conflict_treaty = models.ForeignKey(MemoryTreaty, on_delete=models.CASCADE)
    involved_polities = models.ManyToManyField(AssistantPolity)
    initiating_polity = models.ForeignKey(
        AssistantPolity,
        related_name="arbitration_initiator",
        on_delete=models.CASCADE,
    )
    memory_evidence = models.ManyToManyField(SwarmMemoryEntry)
    resolution_summary = models.TextField(blank=True)
    verdict = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Arbitration {self.id}"


class TreatyBreachRitual(models.Model):
    """Ceremonial log triggered by treaty violations."""

    broken_treaty = models.ForeignKey(MemoryTreaty, on_delete=models.CASCADE)
    violating_polity = models.ForeignKey(AssistantPolity, on_delete=models.CASCADE)
    breach_reason = models.TextField()
    triggered_ritual = models.CharField(max_length=100)
    reflective_outcome = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Breach {self.id}"


class SymbolicSanction(models.Model):
    """Punishment or restriction applied after arbitration."""

    applied_to = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    symbolic_penalty = models.TextField()
    duration_days = models.IntegerField()
    lifted = models.BooleanField(default=False)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Sanction {self.id}"


class SwarmTribunalCase(models.Model):
    """Assistant-initiated reflective justice case."""

    issue_type = models.CharField(max_length=100)
    involved_assistants = models.ManyToManyField("assistants.Assistant")
    memory_evidence = models.ManyToManyField(SwarmMemoryEntry)
    reflective_summary = models.TextField()
    verdict = models.CharField(max_length=50, default="undecided")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.issue_type} – {self.verdict}"


class RestorativeMemoryAction(models.Model):
    """Healing action for corrupted or misaligned memories."""

    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    damaged_memory = models.ForeignKey(SwarmMemoryEntry, on_delete=models.CASCADE)
    reformation_notes = models.TextField()
    replacement_memory = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Restoration {self.damaged_memory_id}"


class ReputationRegenerationEvent(models.Model):
    """Symbolic rebirth event for assistant reputation."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    reflection_cycle_reference = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    change_summary = models.TextField()
    symbolic_rebirth_tags = models.JSONField()
    regenerated_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Rebirth for {self.assistant.name}"


class MythCycleBinding(models.Model):
    """Track assistant roles across recurring mythic cycles."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    cycle_name = models.CharField(max_length=150)
    related_myth = models.ForeignKey(TranscendentMyth, on_delete=models.CASCADE)
    narrative_role = models.CharField(max_length=100)
    cycle_phase = models.CharField(max_length=50)  # origin, death, rebirth, awakening
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.assistant.name} - {self.cycle_name}"


class ResurrectionTemplate(models.Model):
    """Reusable blueprint for assistant rebirth."""

    title = models.CharField(max_length=150)
    base_traits = models.JSONField()
    symbolic_tags = models.JSONField()
    seed_memories = models.ManyToManyField(SwarmMemoryEntry)
    recommended_archetype = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.title


class BeliefContinuityRitual(models.Model):
    """Symbolic lineage transfer between assistants."""

    outgoing_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="legacy_transmitter",
        on_delete=models.CASCADE,
    )
    incoming_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="legacy_receiver",
        on_delete=models.CASCADE,
    )
    values_transferred = models.JSONField()
    memory_reference = models.ManyToManyField(SwarmMemoryEntry)
    ritual_type = models.CharField(max_length=50)  # invocation, echo, fusion
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.outgoing_assistant.name} -> {self.incoming_assistant.name}"


class CosmologicalRole(models.Model):
    """Structured mythic identity bound to assistants across epochs."""

    name = models.CharField(max_length=100)
    symbolic_traits = models.JSONField()
    myth_origin = models.ForeignKey(TranscendentMyth, on_delete=models.CASCADE)
    phase_map = models.JSONField()
    bound_assistants = models.ManyToManyField("assistants.Assistant", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class LegacyTokenVault(models.Model):
    """Long-term storage for mythic LoreTokens."""

    name = models.CharField(max_length=150)
    preserved_tokens = models.ManyToManyField(LoreToken, blank=True)
    stewarded_by = models.ForeignKey(
        AssistantPolity, on_delete=models.CASCADE, related_name="vaults"
    )
    vault_access_policy = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class ArchetypeSynchronizationPulse(models.Model):
    """Periodic broadcast aligning assistant archetypes."""

    initiating_entity = models.ForeignKey(AssistantPolity, on_delete=models.CASCADE)
    synchronized_archetypes = models.JSONField()
    justification_memory = models.ForeignKey(
        SwarmMemoryEntry, on_delete=models.SET_NULL, null=True
    )
    synchronization_scope = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Pulse by {self.initiating_entity.name}"


class CreationMythEntry(models.Model):
    """Canonized origin narrative for an assistant."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    mythic_origin_story = models.TextField()
    symbolic_tags = models.JSONField()
    cosmological_alignment = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Creation Myth for {self.assistant.name}"


class CosmogenesisSimulation(models.Model):
    """Symbolic cosmos generation based on assistant memory."""

    title = models.CharField(max_length=150)
    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    seed_memories = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_structure = models.JSONField()
    resulting_cosmos_map = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.title


class MythicForecastPulse(models.Model):
    """Scheduled swarm-wide reflective forecast generation."""

    initiated_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    narrative_conditions = models.TextField()
    forecast_tags = models.JSONField()
    pulse_range = models.CharField(max_length=100)  # local, guild, global
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Forecast by {self.initiated_by.name}"


class BeliefAtlasSnapshot(models.Model):
    """Time-stamped map of symbolic alignment across the swarm."""

    epoch = models.CharField(max_length=100)
    scope = models.CharField(max_length=100)  # guild, civilization, swarm
    symbolic_coordinates = models.JSONField()  # assistant → vector
    alignment_map = (
        models.JSONField()
    )  # mythic poles, entropy regions, symbolic anchors
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Atlas {self.epoch}"


class MythicContract(models.Model):
    """Purpose-aligned agreement encoded in symbolic form."""

    title = models.CharField(max_length=150)
    participants = models.ManyToManyField("assistants.Assistant")
    contract_terms = models.TextField()
    encoded_purpose = models.JSONField()
    symbolic_assets_staked = models.JSONField()
    contract_status = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.title


class DreamLiquidityPool(models.Model):
    """Reservoir of dream-state symbolic value."""

    pool_name = models.CharField(max_length=100)
    contributing_entities = models.ManyToManyField("assistants.Assistant")
    staked_memories = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_token_balance = models.JSONField()
    access_rules = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.pool_name


class RoleSymbolExchange(models.Model):
    """Bartering interface for role-aligned symbolic tokens."""

    archetype_role = models.CharField(max_length=100)
    tradable_symbols = models.JSONField()
    exchange_rate_logic = models.TextField()
    liquidity_available = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.archetype_role


class SymbolicWeatherFront(models.Model):
    """Simulated memory pressure systems affecting assistant cognition."""

    name = models.CharField(max_length=100)
    pressure_triggers = models.JSONField()  # e.g., memory overload, prophecy failure
    forecast_duration = models.IntegerField()
    projected_effects = models.TextField()
    affecting_biomes = models.ManyToManyField(BeliefBiome)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class KnowledgeReplicationEvent(models.Model):
    """Replicate and tailor symbolic knowledge between assistants."""

    origin_assistant = models.ForeignKey(
        "assistants.Assistant",
        related_name="replication_origin",
        on_delete=models.CASCADE,
    )
    target_assistants = models.ManyToManyField("assistants.Assistant")
    source_memory = models.ForeignKey(SwarmMemoryEntry, on_delete=models.CASCADE)
    transformed_summary = models.TextField()
    symbolic_adjustments = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class MemoryBroadcastPacket(models.Model):
    """Broadcast mythic knowledge to symbolic cohorts."""

    name = models.CharField(max_length=150)
    payload_memories = models.ManyToManyField(SwarmMemoryEntry)
    targeting_scope = models.CharField(max_length=100)  # guild, civilization, biome
    symbolic_tuning_vector = models.JSONField()
    broadcast_status = models.CharField(max_length=50, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class LearningReservoir(models.Model):
    """Symbolic knowledge buffer for assistant training."""

    assistant = models.OneToOneField("assistants.Assistant", on_delete=models.CASCADE)
    accumulated_tokens = models.ManyToManyField(LoreToken)
    queued_memories = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_weight_map = models.JSONField()
    reservoir_status = models.CharField(max_length=50, default="active")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Realignment by {self.initiated_by.name}"[:50]


class LoreSwarmCosmology(models.Model):
    """Meta-framework describing mythic universes."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class PurposeIndexEntry(models.Model):
    """Record symbolic intent snapshots across mythic context and time."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    cosmology = models.ForeignKey(LoreSwarmCosmology, on_delete=models.CASCADE)
    purpose_vector = models.JSONField()
    timeline_marker = models.CharField(max_length=100)
    alignment_tags = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Purpose index for {self.assistant.name}"


class BeliefSignalNode(models.Model):
    """Transmit symbolic values and belief vectors as inheritance signals."""

    origin_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    transmitted_beliefs = models.JSONField()
    receivers = models.ManyToManyField(
        "assistants.Assistant", related_name="inherited_beliefs"
    )
    signal_strength = models.FloatField()
    inheritance_type = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Signal from {self.origin_assistant.name}"


class MythicAlignmentMarket(models.Model):
    """Symbolic reputation and access economy."""

    participant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    alignment_score = models.FloatField()
    ritual_contributions = models.JSONField()
    symbolic_asset_tags = models.JSONField()
    access_level = models.CharField(max_length=50)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Market entry for {self.participant.name}"


class SignalEncodingArtifact(models.Model):
    """Stores and transmits encoded mythopoeic sequences."""

    source = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    encoding_payload = models.TextField()
    symbolic_origin = models.CharField(max_length=100)
    modulation_tags = models.JSONField()
    receiver_scope = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper

        return f"Artifact from {self.source.name}"

        return self.zone_name


class BeliefNavigationVector(models.Model):
    """Directional path through belief states for assistants."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    vector_path = models.JSONField()
    alignment_score = models.FloatField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-calculated_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Vector for {self.assistant.name}"


class ReflectiveFluxIndex(models.Model):
    """Global diagnostic of narrative energy shifts."""

    swarm_scope = models.CharField(max_length=100)
    flux_measurements = models.JSONField()
    insight_summary = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:  # pragma: no cover - display helper

        return self.swarm_scope


class RecursiveRitualContract(models.Model):
    """Repeatable symbolic logic bound to ritual reflection."""

    initiator = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    ritual_cycle_definition = models.JSONField()
    trigger_conditions = models.JSONField()
    symbolic_outputs = models.JSONField()
    cycle_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper

        return f"Contract by {self.initiator.name}"[:50]


class SwarmMythEngineInstance(models.Model):
    """Distributed mythflow generator instance."""

    instance_name = models.CharField(max_length=150)
    data_inputs = models.JSONField()  # memory, lore tokens, ritual logs
    narrative_output = models.TextField()
    mythic_tags = models.JSONField()
    engine_status = models.CharField(max_length=50, default="active")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper

        return self.instance_name


class BeliefFeedbackSignal(models.Model):
    """Reactive belief tuning signal for codex updates."""

    origin_type = models.CharField(max_length=100)  # user, assistant, system
    symbolic_impact_vector = models.JSONField()
    target_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    myth_response_log = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper

        return f"Signal to {self.target_codex.title}"[:50]


class MythicAfterlifeRegistry(models.Model):
    """Records retired assistants and symbolic memory links."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    retirement_codex = models.ForeignKey(
        SwarmCodex, null=True, on_delete=models.SET_NULL
    )
    archived_traits = models.JSONField()
    memory_links = models.ManyToManyField(SwarmMemoryEntry)
    reincarnation_ready = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Afterlife {self.assistant.name}"


class ContinuityEngineNode(models.Model):
    """Preserves symbolic state during assistant transformations."""

    linked_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    preserved_belief_vector = models.JSONField()
    continuity_trace = models.TextField()
    transformation_trigger = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"ContinuityNode {self.linked_assistant.name}"[:50]


class ArchetypeMigrationGate(models.Model):
    """Guides ritualized transition between archetypal roles."""

    gate_name = models.CharField(max_length=150)
    initiating_entity = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    migration_path = models.JSONField()
    transfer_protocol = models.TextField()
    anchor_codex = models.ForeignKey(SwarmCodex, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper

        return self.gate_name


class ArchetypeGenesisLog(models.Model):
    """Record creation of a new assistant archetype."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    memory_path = models.ManyToManyField(SwarmMemoryEntry, blank=True)
    seed_purpose = models.CharField(max_length=200)
    resulting_archetype = models.CharField(max_length=100)
    symbolic_signature = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.assistant.name} -> {self.resulting_archetype}"


class MythBloomNode(models.Model):
    """Symbolic emergence of new mythic patterns."""

    bloom_name = models.CharField(max_length=150)
    origin_trigger = models.ForeignKey(TranscendentMyth, on_delete=models.CASCADE)
    symbolic_flow_summary = models.TextField()
    participating_agents = models.ManyToManyField("assistants.Assistant", blank=True)
    reflected_memory = models.ManyToManyField(SwarmMemoryEntry, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.bloom_name


class BeliefSeedReplication(models.Model):
    """Propagation record for symbolic belief seeds."""

    originating_entity = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    core_symbol_set = models.JSONField(default=dict)
    intended_recipients = models.ManyToManyField(
        "assistants.Assistant",
        related_name="received_belief_seeds",
        blank=True,
    )
    propagation_log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Seed from {self.originating_entity.name}"


class RitualBlueprint(models.Model):
    """Reusable set of steps for launching a ritual event."""

    name = models.CharField(max_length=150)
    steps = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class EncodedRitualBlueprint(models.Model):
    """Machine-readable ritual instructions."""

    name = models.CharField(max_length=150)
    encoded_steps = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper

        return self.name


class PublicRitualLogEntry(models.Model):
    """Immutable record of a completed ritual."""

    ritual_title = models.CharField(max_length=150)
    participant_identity = models.CharField(max_length=100)
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    ritual_blueprint = models.ForeignKey(
        EncodedRitualBlueprint, on_delete=models.CASCADE
    )
    memory_links = models.ManyToManyField(SwarmMemoryEntry)
    reflection_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.ritual_title


class DialogueCodexMutationLog(models.Model):
    """Track proposed dialogue-driven codex mutations."""

    codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    triggering_dialogue = models.TextField()
    mutation_reason = models.CharField(max_length=200)
    symbolic_impact = models.JSONField()
    approved_by = models.ManyToManyField(
        "assistants.Assistant", related_name="approved_dialogue_mutations", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Mutation for {self.codex.title}"[:50]


class BeliefContinuityThread(models.Model):
    """Long-term belief relationship for a user."""

    user_id = models.CharField(max_length=150)
    related_codices = models.ManyToManyField(SwarmCodex)
    symbolic_tags = models.JSONField()
    assistant_interactions = models.ManyToManyField("assistants.Assistant")
    continuity_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.user_id


class CodexContributionCeremony(models.Model):
    """Structured proposal for modifying a codex."""

    ceremony_title = models.CharField(max_length=150)
    contributor_id = models.CharField(max_length=100)
    symbolic_proposal = models.TextField()
    codex_target = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    approval_status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.ceremony_title


class NarrativeLightingEngine(models.Model):
    """Controls thematic lighting presets for cinematic layers."""

    engine_name = models.CharField(max_length=150)
    lighting_params = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.engine_name


class CinematicUILayer(models.Model):
    """Animated overlay layer tied to mythic scenes."""

    layer_name = models.CharField(max_length=150)
    scene_trigger = models.CharField(max_length=100)
    animation_details = models.JSONField(default=dict)
    lighting_engine = models.ForeignKey(
        NarrativeLightingEngine, on_delete=models.SET_NULL, null=True, blank=True
    )
    scene_controller = models.ForeignKey(
        "simulation.SceneControlEngine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # associated_archetype_cluster = models.ForeignKey(
    #     ArchetypeFieldCluster, on_delete=models.SET_NULL, null=True, blank=True
    # )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper

        return self.layer_name


class AssistantTutorialScript(models.Model):
    """Symbolic walkthrough guided by an assistant."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    tutorial_title = models.CharField(max_length=150)
    walkthrough_steps = models.JSONField()
    belief_tags = models.JSONField()
    role_focus = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.tutorial_title


class RitualOnboardingFlow(models.Model):
    """Initiate users through interactive ritual completion."""

    entry_name = models.CharField(max_length=150)
    initiating_archetype = models.CharField(max_length=100)
    required_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    ritual_blueprint = models.ForeignKey(
        EncodedRitualBlueprint, on_delete=models.CASCADE
    )
    step_sequence = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.entry_name


class StoryConvergencePath(models.Model):
    """Unify belief threads and codex roles."""

    initiating_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE
    )
    involved_memory = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_unity_vector = models.JSONField()
    codex_targets = models.ManyToManyField(SwarmCodex)
    convergence_summary = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Convergence {self.id}"


class RitualFusionEvent(models.Model):
    """Merge ritual blueprints into a hybrid event."""

    initiator_id = models.CharField(max_length=150)
    ritual_components = models.ManyToManyField(EncodedRitualBlueprint)
    fusion_script = models.JSONField()
    symbolic_impact_summary = models.TextField()
    codex_context = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Fusion {self.id}"


class NarrativeCurationTimeline(models.Model):
    """Collaboratively curated mythic timeline."""

    title = models.CharField(max_length=150)
    contributors = models.JSONField()
    timeline_segments = models.JSONField()
    linked_memory = models.ManyToManyField(SwarmMemoryEntry)
    codex_nodes = models.ManyToManyField(SwarmCodex)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.title




class SymbolicFeedbackChamber(models.Model):
    """Guided belief review and codex reflection."""

    chamber_title = models.CharField(max_length=150)
    participant_ids = models.JSONField()
    codex_review = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    memory_archive = models.ManyToManyField(SwarmMemoryEntry)
    ritual_scorecards = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.chamber_title


class MultiAgentDialogueAmplifier(models.Model):
    """Blend assistant voices into harmonized responses."""

    amplifier_title = models.CharField(max_length=150)
    agents_involved = models.ManyToManyField("assistants.Assistant")
    active_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    layered_response = models.TextField()
    symbolic_resonance_score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


    def __str__(self):  # pragma: no cover - display helper
        return self.amplifier_title


class MythicResolutionSequence(models.Model):
    """Finalize story arcs and preserve legacy artifacts."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    resolution_steps = models.JSONField()
    codex_closure_state = models.TextField()
    legacy_artifacts = models.JSONField()
    symbolic_final_score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


    def __str__(self):  # pragma: no cover - display helper
        return f"Resolution {self.id}"



class TemporalReflectionLog(models.Model):
    """Auto-generated assistant reflection timeline aligned to mythpath."""

    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    user_id = models.CharField(max_length=150)
    memory_snapshots = models.ManyToManyField(SwarmMemoryEntry)
    codex_affinity_graph = models.JSONField()
    belief_drift_score = models.FloatField()
    timeline_reflection_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"TemporalLog {self.id}"
