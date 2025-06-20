import uuid
from django.db import models
from django.utils.text import slugify
from pgvector.django import VectorField
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class Prompt(models.Model):
    """
    Stores standardized system/user/assistant prompts for semantic search and retrieval.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True)
    type = models.CharField(
        max_length=50,
        choices=[("system", "System"), ("user", "User"), ("assistant", "Assistant")],
        default="system",
    )

    model_backend = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Preferred model or backend to run this prompt (e.g. openai:gpt-4o, claude-3, mistral)",
    )

    format_hint = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Optional rendering or input format (e.g. json, markdown, yaml, chat)",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="remixes",
        help_text="If this prompt is a remix, points to the original",
    )
    content = models.TextField()
    source = models.CharField(max_length=255)
    tags = models.ManyToManyField(
        "mcp_core.Tag", related_name="prompt_links", blank=True
    )
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    complexity = models.FloatField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)
    tone = models.CharField(max_length=100, null=True, blank=True)
    token_count = models.IntegerField(default=0)

    assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="linked_prompts",
    )
    source_document = models.ForeignKey(
        "intel_core.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="prompts",
    )

    flesch_reading_ease = models.FloatField(null=True, blank=True)
    flesch_kincaid_grade = models.FloatField(null=True, blank=True)
    avg_sentence_length = models.FloatField(null=True, blank=True)
    avg_syllables_per_word = models.FloatField(null=True, blank=True)
    reading_time_seconds = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:40]
            self.slug = f"{base_slug}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} - {self.title}"


class PromptPreferences(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prompt_preferences",
    )
    auto_mode_enabled = models.BooleanField(default=False)
    default_trim_threshold = models.IntegerField(null=True, blank=True)
    excluded_sections = ArrayField(
        base_field=models.IntegerField(),
        blank=True,
        default=list,
        help_text="Paragraph indexes to exclude by default",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"


class PromptUsageTemplate(models.Model):
    TRIGGER_CHOICES = [
        ("on_start", "On Assistant Start"),
        ("on_message", "On User Message"),
        ("on_reflection", "On Reflection Cycle"),
        ("on_task", "On Task Execution"),
        ("custom", "Custom Trigger"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    prompt = models.ForeignKey(
        "prompts.Prompt",
        on_delete=models.CASCADE,
        related_name="usage_templates",
    )
    agent = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="prompt_templates",
    )
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)
    fallback_text = models.TextField(blank=True, null=True)

    role = models.CharField(
        max_length=50,
        choices=[("system", "System"), ("user", "User"), ("assistant", "Assistant")],
        default="system",
        help_text="Role this prompt plays in chat sequence",
    )
    model_override = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Force this prompt to run on a specific model (e.g. gpt-4o, mistral-7b)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["agent", "priority", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.trigger_type}) for {self.agent.name}"


class PromptMutationLog(models.Model):
    """Track changes to prompts and their lineage."""
    original_prompt = models.ForeignKey(
        Prompt, on_delete=models.CASCADE, related_name="mutation_logs"
    )
    mutated_text = models.TextField()
    mode = models.CharField(max_length=50)
    tone = models.CharField(max_length=50, null=True, blank=True)
    response_tokens = models.IntegerField(null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="prompt_mutations",
    )
    source_prompt = models.ForeignKey(
        Prompt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="original_mutations",
    )
    mutated_prompt = models.ForeignKey(
        Prompt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mutated_versions",
    )
    mutation_reason = models.TextField(blank=True)
    triggered_by_reflection = models.ForeignKey(
        "assistants.AssistantReflectionLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Mutation of {self.original_prompt.slug} via {self.mode}"


class PromptFeedbackVector(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    feedback_score = models.FloatField()
    source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PromptMutationEffectTrace(models.Model):
    mutation = models.ForeignKey(PromptMutationLog, on_delete=models.CASCADE)
    feedback_vector = models.ForeignKey(
        PromptFeedbackVector, null=True, blank=True, on_delete=models.SET_NULL
    )
    effect_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PromptCapsule(models.Model):
    """Reusable prompt capsule for cross-assistant injection."""

    title = models.CharField(max_length=255)
    content = models.TextField()
    context = models.TextField(blank=True)
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    feedback_rating = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CapsuleTransferLog(models.Model):
    """Log propagation of a prompt capsule between assistants."""

    capsule = models.ForeignKey(
        PromptCapsule, on_delete=models.CASCADE, related_name="transfers"
    )
    from_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="capsule_transfers_out",
    )
    to_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="capsule_transfers_in",
    )
    tag_overwrite = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
