import uuid
from tools.models import Tool
from .core import THOUGHT_TYPES, THOUGHT_MODES, ROLE_CHOICES
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from pgvector.django import VectorField
from django.core.exceptions import ValidationError
from django.utils import timezone
from assistants.constants import THOUGHT_CATEGORY_CHOICES
from .core import Assistant
from memory.models import MemoryEntry
from mcp_core.models import Tag
from story.models import NarrativeEvent
from storyboard.models import NarrativeEvent as StoryboardEvent

class AssistantThoughtLog(models.Model):
    """Record of thoughts generated during assistant reasoning.

    Links the entry to an assistant, project, and related memory."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "Assistant",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="thoughts",
    )

    category = models.CharField(
        max_length=20, choices=THOUGHT_CATEGORY_CHOICES, default="other"
    )
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    project = models.ForeignKey(
        "project.Project",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="thoughts",
    )
    thought_type = models.CharField(
        max_length=30, choices=THOUGHT_TYPES, default="generated"
    )
    thought = models.TextField()
    thought_trace = models.TextField(blank=True, default="")
    linked_memory = models.ForeignKey(
        "memory.MemoryEntry", null=True, blank=True, on_delete=models.SET_NULL
    )
    linked_memories = models.ManyToManyField(
        "memory.MemoryEntry", blank=True, related_name="thought_links"
    )
    linked_reflection = models.ForeignKey(
        "assistants.AssistantReflectionLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thoughts",
    )
    linked_event = models.ForeignKey(
        "story.NarrativeEvent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thought_logs",
    )
    parent_thought = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mutations",
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="assistant"
    )  # 👈 NEW
    mode = models.CharField(max_length=20, choices=THOUGHT_MODES, default="default")
    feedback = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[
            ("perfect", "Perfect"),
            ("helpful", "Helpful"),
            ("not_helpful", "Not Helpful"),
            ("too_long", "Too Long"),
            ("too_short", "Too Short"),
            ("irrelevant", "Irrelevant"),
            ("unclear", "Unclear"),
        ],
    )
    mood = models.CharField(max_length=20, default="neutral", blank=True)
    mood_snapshot = models.JSONField(null=True, blank=True)
    event = models.CharField(max_length=50, null=True, blank=True)
    source_reason = models.CharField(max_length=20, null=True, blank=True)
    fallback_reason = models.CharField(max_length=50, null=True, blank=True)
    fallback_details = models.JSONField(null=True, blank=True)
    tags = models.ManyToManyField(
        "mcp_core.Tag", blank=True, related_name="assistant_thoughts"
    )
    linked_event = models.ForeignKey(
        "storyboard.NarrativeEvent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thought_logs",
    )
    origin = models.CharField(max_length=50, null=True, blank=True)
    tool_used = models.ForeignKey(
        "tools.Tool",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thought_logs",
    )
    tool_result_summary = models.CharField(max_length=255, null=True, blank=True)

    # Empathy tracing
    empathy_response = models.CharField(max_length=255, null=True, blank=True)
    resonated_with_user = models.BooleanField(default=False)

    clarification_needed = models.BooleanField(default=False)
    clarification_prompt = models.TextField(null=True, blank=True)
    summoned_memory_ids = ArrayField(models.UUIDField(), default=list, blank=True)

    narrative_thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thoughts",
    )
    replayed_thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replay_thoughts",
    )
    is_auto_generated = models.BooleanField(default=False)
    coherence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"🧠 {self.thought[:40]}..."

    def clean(self):
        if not self.assistant and not self.project:
            raise ValidationError(
                "Thought must be linked to either an assistant or a project."
            )


class EmotionalResonanceLog(models.Model):
    """Detected emotional resonance for a memory entry."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="emotional_resonance_logs",
    )
    source_memory = models.ForeignKey(
        "memory.MemoryEntry",
        on_delete=models.CASCADE,
        related_name="emotional_resonances",
    )
    detected_emotion = models.CharField(max_length=50)
    intensity = models.FloatField(default=0.0)
    comment = models.TextField(blank=True, null=True)
    context_tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CollaborationLog(models.Model):
    """Snapshot of collaboration moods and conflicts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(
        "assistants.Assistant", related_name="collaboration_logs"
    )
    project = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, related_name="collaboration_logs"
    )
    mood_state = models.CharField(max_length=255, blank=True)
    style_conflict_detected = models.BooleanField(default=False)
    resolution_action = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CollaborationThread(models.Model):
    """Ongoing conversation thread between multiple assistants."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="led_collaboration_threads",
    )
    participants = models.ManyToManyField(
        "assistants.Assistant",
        related_name="collaboration_threads",
        blank=True,
    )
    messages = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]



