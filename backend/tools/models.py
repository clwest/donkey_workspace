from django.db import models
from django.contrib.postgres.fields import ArrayField


class Tool(models.Model):
    """Represents an executable tool integration."""

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    # Include all fields from both versions
    module_path = models.CharField(max_length=255)
    function_name = models.CharField(
        max_length=100,
        default="",          # ← one‐time default for existing + future rows
        help_text="Name of the tool function"
    )
    input_schema = models.JSONField(default=dict, blank=True)
    output_schema = models.JSONField(default=dict, blank=True)
    schema = models.JSONField(blank=True, null=True)

    is_enabled = models.BooleanField(default=True)
    agent_only = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_verified = models.DateTimeField(null=True, blank=True)
    tags = ArrayField(models.CharField(max_length=50), default=list)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ToolUsageLog(models.Model):
    """Record of a tool invocation by an assistant or agent."""

    STATUS_CHOICES = [
        ("success", "Success"),
        ("error", "Error"),
    ]

    FEEDBACK_CHOICES = [
        ("perfect", "Perfect"),
        ("helpful", "Helpful"),
        ("not_helpful", "Not Helpful"),
        ("irrelevant", "Irrelevant"),
        ("error", "Error"),
    ]

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="logs")
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True)
    agent = models.ForeignKey("agents.Agent", on_delete=models.SET_NULL, null=True, blank=True)

    input_payload = models.JSONField()
    output_payload = models.JSONField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="success")

    feedback = models.CharField(
        max_length=20, choices=FEEDBACK_CHOICES, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tool.slug} ({'ok' if self.success else 'fail'})"


class ToolScore(models.Model):
    """Tracks tool performance per assistant with contextual tags."""

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="scores")
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE, related_name="tool_scores")

    score = models.FloatField(default=0.0)
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)
    context_tags = ArrayField(models.CharField(max_length=50), default=list)

    class Meta:
        unique_together = ("tool", "assistant")

    def __str__(self):
        return f"{self.tool.slug} -> {self.assistant.slug}: {self.score}"


class ToolDiscoveryLog(models.Model):
    """Records tool autodiscovery results for auditing."""

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="discoveries", null=True, blank=True)
    path = models.CharField(max_length=255)
    success = models.BooleanField(default=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tool.slug} discovered" if self.tool else self.path
