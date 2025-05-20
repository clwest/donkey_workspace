from django.db import models
import uuid


class DelegationEventManager(models.Manager):
    """Manager with helper for recent events."""

    def recent_delegation_events(self, limit: int = 10):
        return self.order_by("-created_at")[:limit]


from memory.models import MemoryEntry
from prompts.models import Prompt
from project.models import ProjectTask, ProjectMilestone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Used for structured memory and assistant sessions

# --- Choice Constants ---
THOUGHT_TYPES = [
    ("user", "User Input"),
    ("cot", "Chain of Thought"),
    ("generated", "Generated Thought"),
    ("planning", "Planning Step"),
    ("reflection", "Reflection"),
    ("mutation", "Mutation"),
]

MEMORY_MODES = [
    ("none", "None"),
    ("session", "Session"),
    ("long_term", "Long-Term"),
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

THOUGHT_CATEGORY_CHOICES = [
    ("observation", "Observation"),
    ("insight", "Insight"),
    ("idea", "Idea"),
    ("question", "Question"),
    ("goal", "Goal"),
    ("warning", "Warning"),
    ("other", "Other"),
]

# Planning history event types
PLANNING_EVENT_TYPES = [
    ("objective_added", "Objective Added"),
    ("task_modified", "Task Modified"),
    ("milestone_completed", "Milestone Completed"),
    ("reflection_recorded", "Reflection Recorded"),
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
    preferred_model = models.CharField(max_length=100, default="gpt-4o")
    memory_mode = models.CharField(
        max_length=200, choices=MEMORY_MODES, default="long_term"
    )
    embedding = VectorField(
        dimensions=1536, null=True, blank=True
    )  # adjust dim if needed
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


class DelegationStrategy(models.Model):
    """Preferences for how an assistant delegates work to agents."""

    assistant = models.OneToOneField(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="delegation_strategy"
    )
    prefer_specialists = models.BooleanField(default=True)
    trust_threshold = models.FloatField(default=0.75)
    avoid_recent_failures = models.BooleanField(default=True)
    max_active_delegations = models.IntegerField(default=5)

    def __str__(self):
        return f"Strategy for {self.assistant.name}"


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
        max_length=20, choices=THOUGHT_TYPES, default="generated"
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
    tags = models.ManyToManyField(
        "mcp_core.Tag", blank=True, related_name="assistant_thoughts"
    )

    narrative_thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thoughts",
    )
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


class AssistantProject(models.Model):
    """Project workspace tied to a single assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "Assistant", on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=255)
    goal = models.TextField(
        blank=True,
        default="",
        help_text="Main goal or objective for this assistant project.",
    )
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(  # ✅ NEW
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistant_projects",
    )
    status = models.CharField(max_length=50, default="active")
    summary = models.TextField(blank=True, null=True)
    documents = models.ManyToManyField("intel_core.Document", blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assistant", "title")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.assistant.name})"


class AssistantProjectRole(models.Model):
    """Assign assistants to projects with specific roles."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="project_roles"
    )
    project = models.ForeignKey(
        "assistants.AssistantProject", on_delete=models.CASCADE, related_name="roles"
    )
    role_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assistant", "project")

    def __str__(self):
        return f"{self.assistant.name} as {self.role_name}"


class AssistantTask(models.Model):
    """Individual task within an assistant project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "assistants.AssistantProject", on_delete=models.CASCADE, related_name="tasks"
    )
    objective = models.ForeignKey(
        "assistants.AssistantObjective",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="pending")
    notes = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    source_type = models.CharField(
        max_length=20,
        choices=[("thought", "Thought"), ("memory", "Memory"), ("custom", "Custom")],
        default="custom",
    )
    source_id = models.UUIDField(null=True, blank=True)
    proposed_by = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks_proposed",
    )
    assigned_assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks_assigned",
    )
    confirmed_by_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class AssistantReflectionLog(models.Model):
    """Summary of a reflection cycle linked to either an assistant or project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        "assistants.AssistantProject",
        related_name="reflections",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    assistant = models.ForeignKey(
        "Assistant",
        on_delete=models.CASCADE,
        related_name="reflections",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    summary = models.TextField()
    raw_prompt = models.TextField(null=True, blank=True)
    llm_summary = models.TextField(null=True, blank=True)
    insights = models.TextField(null=True, blank=True)
    mood = models.CharField(max_length=50, null=True, blank=True)

    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    linked_memory = models.ForeignKey(
        "memory.MemoryEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reflections",
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ("self_eval", "Self Evaluation"),
            ("behavior", "Behavior"),
            ("insight", "Insight"),
            ("planning", "Planning"),
            ("meta", "Meta"),
        ],
        default="meta",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reflection on {self.project.title or self.linked_memory.id} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AssistantObjective(models.Model):
    """Goal defined for an assistant project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "AssistantProject",  # ✅ This must be AssistantProject, not just Project
        on_delete=models.CASCADE,
        related_name="objectives",
    )
    assistant = models.ForeignKey(
        "Assistant", on_delete=models.CASCADE, related_name="objectives"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    delegated_assistant = models.ForeignKey(
        "Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delegated_objectives",
    )
    generated_from_reflection = models.ForeignKey(
        "assistants.AssistantReflectionLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_objectives",
    )
    source_memory = models.ForeignKey(
        "memory.MemoryEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_objectives",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AssistantPromptLink(models.Model):
    """Associates a project with a specific prompt."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, related_name="linked_prompts"
    )
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "prompt")

    def __str__(self):
        return f"Prompt link for {self.project.title}: {self.prompt.title}"


class AssistantMemoryChain(models.Model):
    """Sequence of related memories and prompts for a project."""

    MODE_CHOICES = [
        ("automatic", "Automatic"),
        ("manual", "Manual"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, related_name="memory_chains"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="manual")
    filter_tags = models.ManyToManyField(
        "mcp_core.Tag", blank=True, related_name="filtered_memory_chains"
    )
    exclude_types = models.JSONField(default=list, blank=True)
    memories = models.ManyToManyField(MemoryEntry, blank=True)
    prompts = models.ManyToManyField(Prompt, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AssistantReflectionInsight(models.Model):
    """Insight gathered from a reflection linked to a document."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    linked_document = models.ForeignKey("intel_core.Document", on_delete=models.CASCADE)
    text = models.TextField()
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight on {self.linked_document.title} by {self.assistant.name}"


class AssistantNextAction(models.Model):
    """Next step derived from an AssistantObjective."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objective = models.ForeignKey(
        AssistantObjective, on_delete=models.CASCADE, related_name="next_actions"
    )
    content = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ProjectPlanningLog(models.Model):
    """Chronological log of planning events for an assistant project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "assistants.AssistantProject",
        on_delete=models.CASCADE,
        related_name="planning_logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50, choices=PLANNING_EVENT_TYPES)
    summary = models.CharField(max_length=255)

    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.UUIDField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
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


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=DelegationEvent)
def queue_delegation_reflection(sender, instance, created, **kwargs):
    if created:
        from assistants.tasks import reflect_on_delegation

        reflect_on_delegation.delay(str(instance.id))


@receiver(post_save, sender=AssistantObjective)
def log_objective_added(sender, instance, created, **kwargs):
    if created:
        ProjectPlanningLog.objects.create(
            project=instance.project,
            event_type="objective_added",
            summary=f"Objective added: {instance.title}",
            related_object=instance,
        )


@receiver(post_save, sender=ProjectTask)
def log_task_change(sender, instance, created, **kwargs):
    assistant_project = getattr(instance.project, "assistant_project", None)
    if assistant_project:
        ProjectPlanningLog.objects.create(
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
        ProjectPlanningLog.objects.create(
            project=assistant_project,
            event_type=event_type,
            summary=f"Milestone: {instance.title}",
            related_object=instance,
        )


@receiver(post_save, sender=AssistantReflectionLog)
def log_reflection_event(sender, instance, created, **kwargs):
    if created and instance.project:
        ProjectPlanningLog.objects.create(
            project=instance.project,
            event_type="reflection_recorded",
            summary=instance.summary[:200],
            related_object=instance,
        )
