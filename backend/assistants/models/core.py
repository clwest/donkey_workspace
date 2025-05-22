from django.db import models
import uuid


class DelegationEventManager(models.Manager):
    """Manager with helper for recent events."""

    def recent_delegation_events(self, limit: int = 10):
        return self.order_by("-created_at")[:limit]


from memory.models import MemoryEntry
from prompts.models import Prompt
from project.models import ProjectTask, ProjectMilestone
from agents.models import SwarmMemoryEntry, GlobalMissionNode
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.fields import ArrayField
from tools.models import Tool
from pgvector.django import VectorField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from story.models import LoreEntry


class AssistantMythLayer(models.Model):
    """Mythic layer of lore attached to an assistant."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="myth_layers"
    )
    origin_story = models.TextField(blank=True)
    legendary_traits = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"MythLayer for {self.assistant.name}"


# Used for structured memory and assistant sessions

# --- Choice Constants ---
THOUGHT_TYPES = [
    ("user", "User Input"),
    ("cot", "Chain of Thought"),
    ("generated", "Generated Thought"),
    ("planning", "Planning Step"),
    ("reflection", "Reflection"),
    ("mutation", "Mutation"),
    ("self_doubt", "Self Doubt"),
    ("prompt_clarification", "Prompt Clarification"),
    ("delegation_suggestion", "Delegation Suggestion"),
    ("identity_reflection", "Identity Reflection"),
    ("refocus", "Refocus Suggestion"),
    ("regeneration", "Plan Regeneration"),
]

MEMORY_MODES = [
    ("none", "None"),
    ("session", "Session"),
    ("long_term", "Long-Term"),
]

# Persona reasoning style
PERSONA_MODES = [
    ("default", "Default"),
    ("improviser", "Improviser"),
    ("planner", "Planner"),
    ("reflector", "Reflector"),
]

THINKING_STYLES = [
    ("cot", "Chain of Thought"),
    ("direct", "Direct Answer"),
    ("reflective", "Reflective"),
]

# Memory chain retrieval behavior
MEMORY_CHAIN_MODES = [
    ("automatic", "Automatic"),
    ("manual", "Manual"),
]

ROLE_CHOICES = [
    ("user", "User"),
    ("assistant", "Assistant"),
]

from .constants import THOUGHT_CATEGORY_CHOICES

# Thought log modes
THOUGHT_MODES = [
    ("default", "Default"),
    ("dream", "Dream"),
]

COLLABORATION_STYLES = [
    ("harmonizer", "Harmonizer"),
    ("challenger", "Challenger"),
    ("strategist", "Strategist"),
    ("supporter", "Supporter"),
    ("autonomous", "Autonomous"),
]

CONFLICT_RESOLUTIONS = [
    ("pause_and_reflect", "Pause and Reflect"),
    ("delegate_to_mediator", "Delegate to Mediator"),
    ("suppress_and_continue", "Suppress and Continue"),
]

# Planning history event types
PLANNING_EVENT_TYPES = [
    ("objective_added", "Objective Added"),
    ("task_modified", "Task Modified"),
    ("milestone_completed", "Milestone Completed"),
    ("reflection_recorded", "Reflection Recorded"),
    ("plan_regenerated", "Plan Regenerated"),
]


# --- Models ---
class Assistant(models.Model):
    """Core AI assistant configuration with optional parent link.

    Holds personality traits, preferred model, and related documents."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    specialty = models.TextField()
    is_active = models.BooleanField(default=True)
    is_demo = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    is_ephemeral = models.BooleanField(default=False)
    expiration_event = models.ForeignKey(
        SwarmMemoryEntry,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ephemeral_assistants",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.URLField(blank=True, null=True)
    system_prompt = models.ForeignKey(
        "prompts.Prompt",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assistants_using_prompt",
    )

    parent_assistant = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sub_assistants",
    )
    personality = models.TextField(max_length=300, blank=True, null=True)
    tone = models.CharField(max_length=300, blank=True, null=True)
    created_from_mood = models.CharField(max_length=20, null=True, blank=True)
    inherited_tone = models.CharField(max_length=20, null=True, blank=True)
    persona_summary = models.TextField(blank=True, null=True)
    personality_description = models.TextField(blank=True, null=True)
    traits = models.JSONField(default=list, blank=True)
    persona_mode = models.CharField(
        max_length=20, choices=PERSONA_MODES, default="default"
    )
    default_memory_chain = models.ForeignKey(
        "assistants.AssistantMemoryChain",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="default_for_assistants",
    )
    capabilities = models.TextField(blank=True)
    capability_embedding = VectorField(dimensions=1536, null=True, blank=True)
    motto = models.CharField(max_length=200, blank=True)
    values = models.JSONField(default=list, blank=True)
    mood_stability_index = models.FloatField(default=1.0)
    last_mood_shift = models.DateTimeField(null=True, blank=True)

    # Empathy metrics
    avg_empathy_score = models.FloatField(default=0.0)
    empathy_tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    preferred_scene_tags = ArrayField(
        models.CharField(max_length=50), default=list, blank=True
    )
    preferred_model = models.CharField(max_length=100, default="gpt-4o")
    memory_mode = models.CharField(
        max_length=200, choices=MEMORY_MODES, default="long_term"
    )
    embedding = VectorField(
        dimensions=1536, null=True, blank=True
    )  # adjust dim if needed
    initial_embedding = VectorField(dimensions=1536, null=True, blank=True)
    last_drift_check = models.DateTimeField(null=True, blank=True)
    needs_recovery = models.BooleanField(default=False)
    documents = models.ManyToManyField(
        "intel_core.Document", blank=True, related_name="linked_assistants"
    )
    current_project = models.ForeignKey(
        "assistants.AssistantProject",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="active_assistants",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistants_created",
    )
    thinking_style = models.CharField(
        max_length=200, choices=THINKING_STYLES, default="cot"
    )

    delegation_threshold_tokens = models.IntegerField(null=True, blank=True)
    auto_delegate_on_feedback = ArrayField(
        models.CharField(max_length=50), null=True, blank=True
    )
    live_relay_enabled = models.BooleanField(default=False)
    memory_summon_enabled = models.BooleanField(default=False)
    collaboration_style = models.CharField(
        max_length=20,
        choices=COLLABORATION_STYLES,
        default="supporter",
    )
    preferred_conflict_resolution = models.CharField(
        max_length=30,
        choices=CONFLICT_RESOLUTIONS,
        default="pause_and_reflect",
    )

    belief_vector = models.JSONField(default=dict, blank=True)

    ideology = models.JSONField(default=dict, blank=True)
    is_alignment_flexible = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while Assistant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug

        self.full_clean()
        super().save(*args, **kwargs)

        if not self.initial_embedding and self.embedding is not None:
            Assistant.objects.filter(id=self.id).update(
                initial_embedding=self.embedding
            )

        if self.is_primary:
            AssistantThoughtLog.objects.get_or_create(
                assistant=self,
                thought_type="meta",
                category="meta",
                thought="I have been assigned as the system’s primary orchestrator. My role is to monitor and coordinate all assistant activity.",
            )

    def __str__(self):
        return self.name

    def clean(self):
        if self.is_primary:
            existing = Assistant.objects.filter(is_primary=True).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Only one assistant can be primary.")

    def get_identity_prompt(self) -> str:
        parts = []
        if self.persona_summary:
            parts.append(f"Persona summary: {self.persona_summary}")
        if self.traits:
            trait_list = []
            if isinstance(self.traits, dict):
                trait_list = [k for k, v in self.traits.items() if v]
            else:
                trait_list = list(self.traits)
            parts.append("Traits: " + ", ".join(trait_list))
        if self.personality_description:
            parts.append(self.personality_description)
        if self.tone:
            parts.append(f"Tone: {self.tone}")
        if self.persona_mode:
            parts.append(f"Mode: {self.persona_mode}")
        if self.values:
            parts.append("Values: " + ", ".join(self.values))
        if self.motto:
            parts.append(f'Motto: "{self.motto}"')
        return " \n".join(parts)

    def record_mood_shift(self, new_mood: str):
        """Update mood stability metrics when the assistant's mood changes."""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        last_log = self.thoughts.order_by("-created_at").first()
        prev_mood = getattr(last_log, "mood", None)
        if prev_mood != new_mood:
            self.last_mood_shift = now

        since = now - timedelta(hours=24)
        moods = (
            self.thoughts.filter(created_at__gte=since)
            .order_by("created_at")
            .values_list("mood", flat=True)
        )
        shifts = 0
        last = None
        for m in moods:
            if last is not None and m != last:
                shifts += 1
            last = m

        index = 1.0 - min(shifts, 5) * 0.2
        if (
            prev_mood
            and prev_mood != new_mood
            and {prev_mood, new_mood}
            in [
                {"playful", "urgent"},
                {"optimistic", "anxious"},
            ]
        ):
            index -= 0.1

        if self.last_mood_shift and now - self.last_mood_shift > timedelta(hours=1):
            index = min(1.0, index + 0.05)

        self.mood_stability_index = round(max(index, 0.0), 2)
        self.save(update_fields=["mood_stability_index", "last_mood_shift"])

    def check_expiration(self):
        """Deactivate the assistant if its expiration event has passed."""
        if self.is_ephemeral and self.expiration_event:
            if timezone.now() >= self.expiration_event.created_at and self.is_active:
                self.is_active = False
                self.save(update_fields=["is_active"])

    def generate_insight_plan(self, context_filter: str = "") -> list[str]:
        """Return a basic plan derived from stored insights."""
        base = (
            f"Review context: {context_filter}"
            if context_filter
            else "Review recent insights"
        )
        return [base, "Outline key tasks", "Share plan with team"]


class DelegationStrategy(models.Model):
    """Preferences for how an assistant delegates work to agents."""

    assistant = models.OneToOneField(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="delegation_strategy",
    )
    prefer_specialists = models.BooleanField(default=True)
    trust_threshold = models.FloatField(default=0.75)
    avoid_recent_failures = models.BooleanField(default=True)
    max_active_delegations = models.IntegerField(default=5)

    def __str__(self):
        return f"Strategy for {self.assistant.name}"


class AssistantSkill(models.Model):
    """Skill or capability associated with an assistant."""

    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="skills",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    confidence = models.FloatField(default=0.5)
    related_tools = models.ManyToManyField("tools.Tool", blank=True)
    related_tags = ArrayField(models.CharField(max_length=50), default=list)

    class Meta:
        unique_together = ("assistant", "name")

    def __str__(self) -> str:  # pragma: no cover - display
        return f"{self.assistant.name}: {self.name}"


