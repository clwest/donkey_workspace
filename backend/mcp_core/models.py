from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.conf import settings

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from prompts.models import Prompt, PromptUsageTemplate
from intel_core.models import Document
import uuid
from pgvector.django import VectorField
from django.utils.text import slugify
from prompts.utils.token_helpers import EMBEDDING_MODEL

EMBEDDING_LENGTH = 1536

User = settings.AUTH_USER_MODEL


class MemoryContext(models.Model):
    target_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True
    )
    target_object_id = models.UUIDField(null=True)
    target = GenericForeignKey("target_content_type", "target_object_id")

    content = models.TextField()
    important = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True, null=True)
    tags = models.ManyToManyField("Tag", blank=True, related_name="memory_contexts")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Memory [{self.target_content_type}] - {self.content[:50]}"

    @property
    def target_type(self):
        return self.target_content_type.model if self.target_content_type else None

    @property
    def target_id(self):
        return str(self.target_object_id) if self.target_object_id else None


class Plan(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    memory_context = models.ForeignKey(
        MemoryContext, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("blocked", "Blocked"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="open")
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True
    )
    project = models.CharField(max_length=255, blank=True, null=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title


class Fault(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("fixed", "Fixed"),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="faults")
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fault in {self.task.title}"


class ActionLog(models.Model):
    ACTION_TYPES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("assign", "Assign"),
        ("complete", "Complete"),
        ("reflect", "Reflect"),
    ]

    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    related_agent = models.ForeignKey(
        "agents.Agent", on_delete=models.SET_NULL, null=True, blank=True
    )
    related_task = models.ForeignKey(
        Task, on_delete=models.SET_NULL, null=True, blank=True
    )
    related_plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} - {self.description[:50]}"


class PromptUsageLog(models.Model):
    prompt_slug = models.SlugField()
    prompt_title = models.CharField(max_length=255)
    prompt = models.ForeignKey(
        Prompt,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="usage_logs",
    )
    template = models.ForeignKey(
        PromptUsageTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="usage_logs",
    )

    used_by = models.CharField(
        max_length=100,
        help_text="E.g., character creation, image generation, assistant reply",
    )
    assistant_id = models.UUIDField(null=True, blank=True)

    input_context = models.TextField(blank=True)
    rendered_prompt = models.TextField()
    result_output = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    purpose = models.CharField(max_length=100, null=True, blank=True)
    context_id = models.CharField(max_length=255, null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["prompt_slug"]),
            models.Index(fields=["used_by"]),
        ]

    def __str__(self):
        return f"{self.prompt_title} used in {self.used_by} at {self.created_at}"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(
        max_length=10, blank=True, null=True, help_text="Optional HEX color"
    )
    embedding = VectorField(dimensions=EMBEDDING_LENGTH, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class NarrativeThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField("Tag", blank=True, related_name="narrative_threads")
    documents = models.ManyToManyField(
        Document, blank=True, related_name="threads"
    )  # ✅ Add this line
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    mood_at_creation = models.CharField(max_length=20, null=True, blank=True)
    avg_mood = models.CharField(max_length=20, null=True, blank=True)
    last_refocus_prompt = models.DateTimeField(null=True, blank=True)
    related_memories = models.ManyToManyField(
        "memory.MemoryEntry", related_name="related_threads", blank=True
    )
    origin_memory = models.ForeignKey(
        "memory.MemoryEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="origin_threads",
    )
    continuity_score = models.FloatField(null=True, blank=True)
    last_diagnostic_run = models.DateTimeField(null=True, blank=True)
    continuity_summary = models.TextField(null=True, blank=True)
    linked_threads = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="linked_to"
    )
    long_term_objective = models.TextField(blank=True, null=True)
    milestones = models.JSONField(default=list, blank=True)
    completed_milestones = models.JSONField(default=list, blank=True)

    class CompletionStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        STALLED = "stalled", "Stalled"

    completion_status = models.CharField(
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.DRAFT,
    )
    progress_percent = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class DevDoc(models.Model):
    uuid = models.UUIDField(null=True, blank=True, editable=False, unique=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=150)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    source_file = models.CharField(max_length=255, blank=True)
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    reflected_at = models.DateTimeField(null=True, blank=True)

    # 🧠 NEW LINK TO TRUE DOCUMENT
    linked_document = models.ForeignKey(
        "intel_core.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="linked_devdocs",
    )

    linked_assistants = models.ManyToManyField(
        "assistants.Assistant", blank=True, related_name="dev_docs"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-link document if none set
        if not self.linked_document:
            try:
                self.linked_document = Document.objects.get(
                    title__iexact=self.title.strip()
                )
            except Document.DoesNotExist:
                pass  # Optional: log warning if you want

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# mcp_core/models.py
class GroupedDevDocReflection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField()
    raw_json = models.TextField()
    related_docs = models.ManyToManyField("mcp_core.DevDoc", blank=True)
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    source_assistant = models.ForeignKey(
        "assistants.Assistant", null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"Grouped Reflection @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ThreadDiagnosticLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(
        NarrativeThread, on_delete=models.CASCADE, related_name="diagnostics"
    )
    TYPE_CHOICES = [
        ("continuity_diagnostic", "Continuity Diagnostic"),
        ("emotional_diagnostic", "Emotional Diagnostic"),
        ("realignment_suggestion", "Realignment Suggestion"),
    ]

    score = models.FloatField()
    summary = models.TextField()

    type = models.CharField(
        max_length=30, choices=TYPE_CHOICES, default="continuity_diagnostic"
    )
    proposed_changes = models.JSONField(null=True, blank=True)

    mood_influence = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Diagnostic {self.score:.2f} for {self.thread.title}"


class ThreadObjectiveReflection(models.Model):
    """Reflection on progress toward a thread's long-term objective."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(
        NarrativeThread, on_delete=models.CASCADE, related_name="objective_reflections"
    )
    thought = models.TextField()
    created_by = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thread_reflections",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reflection for {self.thread.title} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ThreadSplitLog(models.Model):
    """Record when a memory entry is moved between threads."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_thread = models.ForeignKey(
        NarrativeThread,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="split_from_logs",
    )
    to_thread = models.ForeignKey(
        NarrativeThread,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="split_to_logs",
    )
    moved_entry = models.ForeignKey(
        "memory.MemoryEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="thread_split_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - simple display
        return f"Moved {self.moved_entry_id} -> {self.to_thread_id}"


class ThreadMergeLog(models.Model):
    """Administrative record of merged narrative threads."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_thread = models.ForeignKey(
        NarrativeThread, on_delete=models.CASCADE, related_name="merges_from"
    )
    to_thread = models.ForeignKey(
        NarrativeThread, on_delete=models.CASCADE, related_name="merges_to"
    )
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# class ThreadSplitLog(models.Model):
#     """Record of a thread split operation."""

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     original_thread = models.ForeignKey(
#         NarrativeThread, on_delete=models.CASCADE, related_name="splits_from"
#     )
#     new_thread = models.ForeignKey(
#         NarrativeThread, on_delete=models.CASCADE, related_name="splits_to"
#     )
#     moved_entries = models.JSONField()
#     summary = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)


class PublicEventLog(models.Model):
    """Record a public-facing event in the system."""

    timestamp = models.DateTimeField(auto_now_add=True)
    actor_name = models.CharField(max_length=150)
    event_details = models.TextField()
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        status = "success" if self.success else "failed"
        return f"{self.actor_name} {status} @ {self.timestamp:%Y-%m-%d %H:%M}"
