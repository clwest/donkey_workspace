from django.db import models
import uuid
from memory.models import MemoryEntry
from prompts.models import Prompt
from project.models import ProjectTask, ProjectMilestone
from agents.models.lore import SwarmMemoryEntry, GlobalMissionNode
from assistants.models.project import ProjectPlanningLog
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
from .core import (
    THOUGHT_TYPES,
    MEMORY_MODES,
    PERSONA_MODES,
    THINKING_STYLES,
    MEMORY_CHAIN_MODES,
    ROLE_CHOICES,
    THOUGHT_MODES,
    COLLABORATION_STYLES,
    CONFLICT_RESOLUTIONS,
    PLANNING_EVENT_TYPES,
    DelegationEventManager,
)


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
            from django.apps import apps

            AssistantThoughtLog = apps.get_model("assistants", "AssistantThoughtLog")
            AssistantThoughtLog.objects.get_or_create(
                assistant=self,
                thought_type="meta",
                category="meta",
                thought=(
                    "I have been assigned as the system’s primary orchestrator. My role is to monitor and coordinate all assistant activity."
                ),
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

        return f"{self.event_type} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


# backend/assistants/models.py
class SignalSource(models.Model):
    """External platform or feed monitored for signals."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.CharField(max_length=50)  # e.g., "Twitter", "YouTube", "Blog"
    name = models.CharField(max_length=255)  # e.g., "Pliny the Liberator"
    handle = models.CharField(max_length=255, blank=True, null=True)  # e.g., "@pliny"
    url = models.URLField(blank=True, null=True)
    priority = models.IntegerField(default=5)  # 1=highest priority
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.platform})"


class SignalCatch(models.Model):
    """Captured content from a SignalSource with scoring."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        SignalSource, on_delete=models.CASCADE, related_name="catches"
    )
    original_content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    score = models.FloatField(default=0.0)  # 0-1 confidence that this is meaningful
    is_meaningful = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source.name} — {self.created_at.strftime('%Y-%m-%d')}"


class ChatSession(models.Model):
    """Persistent conversation thread between a user and assistant."""

    id = models.BigAutoField(
        primary_key=True
    )  # Or just omit entirely — Django auto-adds this
    session_id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        null=True,
        blank=True,
    )
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    project = models.ForeignKey(
        "project.Project", on_delete=models.SET_NULL, null=True, blank=True
    )
    memory_chain = models.ForeignKey(
        "assistants.AssistantMemoryChain",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
    )
    narrative_thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="narrative_chat_sessions",
    )
    thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.session_id}"


class StructuredMemory(models.Model):
    """Key-value memory attached to a chat session."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="structured_memories",
    )
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="structured_memories",
        null=True,
        blank=True,
    )
    memory_key = models.CharField(max_length=255)
    memory_value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "session", "memory_key")
        indexes = [
            models.Index(fields=["user", "memory_key"]),
            models.Index(fields=["session", "memory_key"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.memory_key}"


class TokenUsage(models.Model):
    """Tracks token and cost usage for sessions and assistants."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="token_usages",
        null=True,
        blank=True,
    )
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        to_field="session_id",
        related_name="token_usages",
    )
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    total_cost = models.FloatField(default=0.0)
    usage_type = models.CharField(max_length=50)
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    project = models.ForeignKey(
        "project.Project", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.usage_type}"


class AssistantChatMessage(models.Model):
    """Message exchanged within a ChatSession."""

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, null=True, unique=False, db_index=True
    )

    session = models.ForeignKey(
        "ChatSession",
        on_delete=models.CASCADE,
        to_field="session_id",
        related_name="messages",
    )

    role = models.CharField(
        max_length=50, choices=[("user", "User"), ("assistant", "Assistant")]
    )

    content = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=[
            ("text", "Text"),
            ("image", "Image"),
            ("audio", "Audio"),
            ("system", "System"),
        ],
        default="text",
    )
    image_url = models.URLField(null=True, blank=True)
    audio_url = models.URLField(null=True, blank=True)
    tts_model = models.CharField(max_length=100, null=True, blank=True)
    style = models.CharField(max_length=100, null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)

    feedback = models.CharField(
        max_length=50,
        choices=[
            ("helpful", "Helpful"),
            ("not_helpful", "Not Helpful"),
            ("too_long", "Too Long"),
            ("too_short", "Too Short"),
            ("irrelevant", "Irrelevant"),
            ("unclear", "Unclear"),
            ("perfect", "Perfect"),
        ],
        null=True,
        blank=True,
    )

    topic = models.ForeignKey(
        "Topic",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )

    memory = models.ForeignKey(
        "memory.MemoryEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="messages",
    )

    search_vector = SearchVectorField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [GinIndex(fields=["search_vector"])]

    def __str__(self):
        return f"{self.role.title()} Message in {self.session_id}"


class AudioResponse(models.Model):
    """Audio file associated with chat messages."""

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        to_field="session_id",
        related_name="audio_responses",
    )
    user_message = models.ForeignKey(
        AssistantChatMessage,
        on_delete=models.CASCADE,
        related_name="user_audio",
        null=True,
        blank=True,
    )
    assistant_message = models.ForeignKey(
        AssistantChatMessage,
        on_delete=models.CASCADE,
        related_name="assistant_audio",
        null=True,
        blank=True,
    )
    audio_file = models.FileField(upload_to="audio_responses/", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AudioResponse for {self.session_id}"


class Topic(models.Model):
    """Topic of conversation used to tag chat messages."""

    name = models.CharField(max_length=255, unique=True)
    keywords = models.TextField(help_text="Comma-separated keywords")
    description = models.TextField(null=True, blank=True)
    is_universal = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DelegationEvent(models.Model):
    """Record when one assistant delegates to another."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_assistant = models.ForeignKey(
        "Assistant",
        on_delete=models.CASCADE,
        related_name="delegations_made",
    )
    child_assistant = models.ForeignKey(
        "Assistant",
        on_delete=models.CASCADE,
        related_name="delegations_received",
    )
    triggering_memory = models.ForeignKey(
        MemoryEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delegation_events",
    )
    triggering_session = models.ForeignKey(
        "assistants.ChatSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delegation_events",
    )
    objective = models.ForeignKey(
        "assistants.AssistantObjective",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delegation_events",
    )
    triggered_by_tool = models.ForeignKey(
        "tools.Tool",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delegation_events",
    )
    handoff = models.BooleanField(default=False)
    reason = models.TextField()
    summary = models.TextField(blank=True, null=True)
    score = models.IntegerField(null=True, blank=True)
    trust_label = models.CharField(
        max_length=20,
        choices=[
            ("trusted", "Trusted"),
            ("neutral", "Neutral"),
            ("unreliable", "Unreliable"),
        ],
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DelegationEventManager()

    def __str__(self):
        return f"{self.parent_assistant} -> {self.child_assistant}"


class AssistantMessage(models.Model):
    """Direct message sent between assistants."""

    sender = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    recipient = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="messages_received",
    )
    content = models.TextField()
    session = models.ForeignKey(
        "assistants.ChatSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistant_messages",
    )
    related_memory = models.ForeignKey(
        "memory.MemoryEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistant_messages",
    )
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("delivered", "Delivered"), ("seen", "Seen")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class RoutingSuggestionLog(models.Model):
    """Log of assistant routing suggestions and outcomes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context_summary = models.TextField()
    tags = ArrayField(models.CharField(max_length=50), default=list)
    suggested_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routing_suggestions",
    )
    confidence_score = models.FloatField(default=0.0)
    reasoning = models.TextField(blank=True, null=True)
    selected = models.BooleanField(default=False)
    user_feedback = models.CharField(max_length=10, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):  # pragma: no cover - simple display
        return f"{self.suggested_assistant} ({self.confidence_score:.2f})"


class SessionHandoff(models.Model):
    """Record when a chat session is handed off between assistants."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="handoffs_made",
    )
    to_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="handoffs_received",
    )
    session = models.ForeignKey(
        "assistants.ChatSession",
        on_delete=models.CASCADE,
        related_name="handoffs",
        to_field="session_id",
    )
    reason = models.TextField()
    triggering_message = models.ForeignKey(
        "assistants.AssistantChatMessage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handoff_triggers",
    )
    handoff_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_assistant} -> {self.to_assistant} @ {self.session}"


class AssistantSwitchEvent(models.Model):
    """Record when a session is switched to a different assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="switches_from",
    )
    to_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="switches_to",
    )
    from_session = models.ForeignKey(
        "assistants.ChatSession",
        on_delete=models.CASCADE,
        related_name="switch_from_events",
        to_field="session_id",
    )
    to_session = models.ForeignKey(
        "assistants.ChatSession",
        on_delete=models.CASCADE,
        related_name="switch_to_events",
        to_field="session_id",
    )
    narrative_thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistant_switches",
    )
    reason = models.TextField(blank=True)
    automated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_assistant} -> {self.to_assistant}"


class AssistantHandoffLog(models.Model):
    """High-level log when responsibility is transferred between assistants."""

    from_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="handoff_logs_from",
    )
    to_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="handoff_logs_to",
    )
    project = models.ForeignKey(
        "assistants.AssistantProject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handoff_logs",
    )
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.from_assistant} -> {self.to_assistant}"


class SpecializationDriftLog(models.Model):
    """Record detected drift from an assistant's original specialty or prompt."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="drift_logs",
    )
    score = models.FloatField(help_text="Drift score 0..1 where 1=high drift")
    timestamp = models.DateTimeField(auto_now_add=True)
    drift_score = models.FloatField()
    summary = models.TextField()
    trigger_type = models.CharField(max_length=50)
    auto_flagged = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    requires_retraining = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:  # pragma: no cover - display
        return f"{self.assistant.name} drift {self.drift_score:.2f}"


class DebateSession(models.Model):
    """Session tracking a multi-assistant debate."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=255)
    memory = models.ForeignKey(
        "memory.MemoryEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="debate_sessions",
    )
    project = models.ForeignKey(
        "project.Project",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="debate_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover - display
        return self.topic


class DebateThoughtLog(models.Model):
    """Argument or rebuttal from an assistant in a debate session."""

    POSITION_CHOICES = [
        ("agree", "Agree"),
        ("disagree", "Disagree"),
        ("expand", "Expand"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    debate_session = models.ForeignKey(
        DebateSession, on_delete=models.CASCADE, related_name="logs"
    )
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="debate_logs"
    )
    round = models.IntegerField(default=1)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):  # pragma: no cover - display
        return f"{self.assistant.name} {self.position}"


class DebateSummary(models.Model):
    """Final consensus or summary for a debate session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        DebateSession, on_delete=models.CASCADE, related_name="summaries"
    )
    summary = models.TextField()
    created_by = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="debate_summaries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display
        return f"Summary for {self.session.topic}"


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.db.utils import DataError, ProgrammingError


def safe_create_planning_log(project, event_type, summary, related_object=None):
    """Create a ProjectPlanningLog entry, ignoring object_id type mismatches."""
    try:
        ProjectPlanningLog.objects.create(
            project=project,
            event_type=event_type,
            summary=summary,
            related_object=related_object,
        )
    except (DataError, IntegrityError, ProgrammingError, ValueError):
        ProjectPlanningLog.objects.create(
            project=project,
            event_type=event_type,
            summary=summary,
        )


@receiver(post_save, sender=DelegationEvent)
def queue_delegation_reflection(sender, instance, created, **kwargs):
    if created:
        from assistants.tasks import reflect_on_delegation

        reflect_on_delegation.delay(str(instance.id))


@receiver(post_save, sender="assistants.AssistantObjective")
def log_objective_added(sender, instance, created, **kwargs):
    if created:
        safe_create_planning_log(
            project=instance.project,
            event_type="objective_added",
            summary=f"Objective added: {instance.title}",
            related_object=instance,
        )


@receiver(post_save, sender=ProjectTask)
def log_task_change(sender, instance, created, **kwargs):
    assistant_project = getattr(instance.project, "assistant_project", None)
    if assistant_project:
        safe_create_planning_log(
            project=assistant_project,
            event_type="task_modified",
            summary=f"{'Created' if created else 'Updated'} task: {instance.title}",
            related_object=instance,
        )


@receiver(post_save, sender=ProjectMilestone)
def log_milestone_event(sender, instance, created, **kwargs):
    assistant_project = getattr(instance.project, "assistant_project", None)
    if assistant_project and (created or instance.is_completed):
        event_type = "milestone_completed" if instance.is_completed else "task_modified"
        safe_create_planning_log(
            project=assistant_project,
            event_type=event_type,
            summary=f"Milestone: {instance.title}",
            related_object=instance,
        )


@receiver(post_save, sender="assistants.AssistantReflectionLog")
def log_reflection_event(sender, instance, created, **kwargs):
    if created and instance.project:
        safe_create_planning_log(
            project=instance.project,
            event_type="reflection_recorded",
            summary=instance.summary[:200],
            related_object=instance,
        )


@receiver(post_save, sender="assistants.AssistantReflectionLog")
def record_swarm_memory(sender, instance, created, **kwargs):
    if not created:
        return
    entry = SwarmMemoryEntry.objects.create(
        title=instance.title,
        content=instance.summary,
        origin="reflection",
    )
    if instance.project:
        entry.linked_projects.add(instance.project)
        entry.linked_agents.set(list(instance.project.agents.all()))
    if instance.assistant:
        entry.linked_agents.add(*instance.assistant.assigned_agents.all())


class CouncilSession(models.Model):
    """Group of assistants debating or collaborating on a topic."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=255)
    linked_memory = models.ForeignKey(
        "memory.MemoryEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="council_sessions",
    )
    project = models.ForeignKey(
        "project.Project",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="council_sessions",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="council_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("paused", "Paused"), ("finished", "Finished")],
        default="active",
    )
    members = models.ManyToManyField(
        "assistants.Assistant", blank=True, related_name="council_sessions"
    )

    def __str__(self) -> str:  # pragma: no cover - display
        return self.topic


class CouncilThought(models.Model):
    """Individual assistant contribution during a council session."""

    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="council_thoughts",
    )
    council_session = models.ForeignKey(
        CouncilSession,
        on_delete=models.CASCADE,
        related_name="thoughts",
    )
    content = models.TextField()
    round = models.IntegerField(default=1)
    is_final = models.BooleanField(default=False)
    mood = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - display
        return f"{self.assistant} @ {self.council_session}"


class CouncilOutcome(models.Model):
    """Final summary or decision from a council session."""

    council_session = models.OneToOneField(
        CouncilSession,
        on_delete=models.CASCADE,
        related_name="outcome",
    )
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - display
        return f"Outcome for {self.council_session}"


class AssistantCouncil(models.Model):
    """Persistent group of assistants for deliberation and voting."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(
        "assistants.Assistant", related_name="councils", blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class OracleLayer(models.Model):
    """Prophetic advisory memory segment for an assistant."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="oracle_layers"
    )
    memory_focus = models.TextField()
    tone = models.CharField(max_length=50, default="mystic")
    tag_scope = models.JSONField()
    summary_insight = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"OracleLayer for {self.assistant.name}"


class ProphecyNode(models.Model):
    """Predicted event record derived from an oracle layer."""

    source = models.ForeignKey(OracleLayer, on_delete=models.CASCADE)
    encoded_symbols = models.JSONField()
    forecast_window = models.CharField(max_length=50)
    predicted_events = models.TextField()
    accuracy_rating = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Prophecy {self.id}"


class NarrativeDebate(models.Model):
    """Structured debate between assistants from mythic perspectives."""

    topic = models.TextField()
    participants = models.ManyToManyField("assistants.Assistant")
    perspectives = models.JSONField()
    outcome_summary = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - display
        return f"Debate on {self.topic[:30]}..."


class AssistantGuild(models.Model):
    """Belief-aligned guild of assistants."""

    name = models.CharField(max_length=150)
    purpose = models.TextField(blank=True)
    members = models.ManyToManyField("assistants.Assistant", blank=True)
    founding_myth = models.ForeignKey(
        LoreEntry,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="guilds",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class AssistantCivilization(models.Model):
    """Civilization of assistants evolved from mythic lineage."""

    name = models.CharField(max_length=150)
    myth_root = models.ForeignKey(LoreEntry, on_delete=models.CASCADE)
    founding_guilds = models.ManyToManyField(AssistantGuild)
    belief_alignment = models.JSONField(default=dict)
    symbolic_domain = models.TextField()
    legacy_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.name


class AssistantReputation(models.Model):
    """Track lore token influence and peer recognition."""

    assistant = models.OneToOneField(Assistant, on_delete=models.CASCADE)
    tokens_created = models.IntegerField(default=0)
    tokens_endorsed = models.IntegerField(default=0)
    tokens_received = models.IntegerField(default=0)
    reputation_score = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-reputation_score"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Reputation for {self.assistant.name}"


class ConscienceModule(models.Model):
    """Ethical profile and mythic alignment for an assistant."""

    assistant = models.OneToOneField(
        Assistant, on_delete=models.CASCADE, related_name="conscience"
    )
    core_values = models.JSONField(default=dict, blank=True)
    ethical_constraints = models.JSONField(default=dict, blank=True)
    guiding_myths = models.ManyToManyField(
        "agents.TranscendentMyth", blank=True, related_name="conscience_modules"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Conscience for {self.assistant.name}"


class DecisionFramework(models.Model):
    """Record of myth-weighted decision strategies."""

    assistant = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="decision_frameworks"
    )
    linked_conscience = models.ForeignKey(
        ConscienceModule, on_delete=models.CASCADE, related_name="decisions"
    )
    myth_weight_map = models.JSONField(default=dict, blank=True)
    scenario_description = models.TextField()
    selected_strategy = models.TextField(blank=True)
    evaluation_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Decision {self.id} for {self.assistant.name}"


class PurposeRouteMap(models.Model):
    """Rules for routing memory by purpose or tone."""

    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    input_tags = models.JSONField()
    output_path = models.CharField(max_length=200)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Route for {self.assistant.name}"


class AutonomyNarrativeModel(models.Model):
    """Narrative arc state for an assistant."""

    assistant = models.OneToOneField(Assistant, on_delete=models.CASCADE)
    current_arc = models.CharField(max_length=100)
    known_story_events = models.ManyToManyField(SwarmMemoryEntry)
    active_purpose_statement = models.TextField()


class MythCommunityCluster(models.Model):
    """Community cluster organized around shared mythic themes."""

    cluster_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    member_guilds = models.ManyToManyField("assistants.AssistantGuild", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.cluster_name


class CodexLinkedGuild(models.Model):
    """Assistant guild with a primary codex association."""

    guild_name = models.CharField(max_length=150)
    codex = models.ForeignKey(
        "agents.SwarmCodex",
        on_delete=models.CASCADE,
        related_name="assistant_guilds",
    )
    members = models.ManyToManyField(
        "assistants.Assistant", blank=True, related_name="assistant_guild_memberships"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.guild_name


class AssistantTravelLog(models.Model):
    """Record symbolic and ritual journeys taken by an assistant."""

    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    travel_route = models.JSONField()
    visited_memory = models.ManyToManyField("agents.SwarmMemoryEntry", blank=True)
    symbolic_tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Travel log for {self.assistant.name}"


class SymbolicInfluenceReport(models.Model):
    """Dashboard report of user impact and codex alignment."""

    user_id = models.CharField(max_length=150)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    codex_impact_vector = models.JSONField(default=dict)
    ritual_interaction_stats = models.JSONField(default=dict)
    memory_contributions = models.ManyToManyField("agents.SwarmMemoryEntry", blank=True)
    symbolic_score_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Influence for {self.user_id}"
