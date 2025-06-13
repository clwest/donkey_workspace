import uuid
from django.db import models
from django.conf import settings


class AssistantReflectionLog(models.Model):
    """Summary of a reflection cycle linked to either an assistant or project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    project = models.ForeignKey(
        "assistants.AssistantProject",
        related_name="project_reflections",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    assistant = models.ForeignKey(
        "Assistant",
        on_delete=models.CASCADE,
        related_name="assistant_reflections",
        null=True,
        blank=True,
    )

    document = models.ForeignKey(
        "intel_core.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reflections",
    )

    title = models.CharField(max_length=255)
    summary = models.TextField(default="", blank=True, null=False)
    raw_prompt = models.TextField(null=True, blank=True)
    llm_summary = models.TextField(null=True, blank=True)
    insights = models.TextField(null=True, blank=True)
    mood = models.CharField(max_length=50, null=True, blank=True)

    document_section = models.CharField(max_length=120, null=True, blank=True)
    group_slug = models.SlugField(max_length=120, null=True, blank=True)
    is_summary = models.BooleanField(default=False)

    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    related_chunks = models.ManyToManyField(
        "intel_core.DocumentChunk", blank=True, related_name="reflection_logs"
    )
    related_anchors = models.ManyToManyField(
        "memory.SymbolicMemoryAnchor", blank=True, related_name="related_reflections"
    )
    anchor = models.ForeignKey(
        "memory.SymbolicMemoryAnchor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reflection_logs",
    )
    is_primer = models.BooleanField(default=False)
    generated_from_memory_ids = models.JSONField(default=list, blank=True)
    linked_memory = models.ForeignKey(
        "memory.MemoryEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memory_reflections",
    )
    linked_event = models.ForeignKey(
        "story.NarrativeEvent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reflection_logs",
    )
    demo_reflection = models.BooleanField(default=False)
    prompt_log = models.ForeignKey(
        "mcp_core.PromptUsageLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reflection_logs",
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
        if self.project:
            target = self.project.title
        elif self.linked_memory:
            target = str(self.linked_memory.id)
        else:
            target = "unknown"
        return f"Reflection on {target} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AssistantReflectionInsight(models.Model):
    """Insight gathered from a reflection linked to a document."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    linked_document = models.ForeignKey("intel_core.Document", on_delete=models.CASCADE)
    text = models.TextField()
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    chunks = models.ManyToManyField(
        "intel_core.DocumentChunk", blank=True, related_name="reflection_insights"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight on {self.linked_document.title} by {self.assistant.name}"


class ReflectionGroup(models.Model):
    """Group reflections across multiple documents for an assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="reflection_groups",
    )
    linked_assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="linked_reflection_groups",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_reflection_groups",
    )
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=255, blank=True)
    documents = models.ManyToManyField(
        "intel_core.Document", blank=True, related_name="reflection_groups"
    )
    document_count = models.PositiveIntegerField(default=0)
    reflections = models.ManyToManyField(
        AssistantReflectionLog, blank=True, related_name="groups"
    )
    summary = models.TextField(blank=True, default="")
    summary_text = models.TextField(blank=True, default="")
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    summary_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-summary_updated", "-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.title or self.slug


class BirthReflectionAttempt(models.Model):
    """Track each retry attempt for an assistant birth reflection."""

    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="birth_attempts",
    )
    status = models.CharField(max_length=20)
    error_message = models.TextField(null=True, blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attempted_at"]
