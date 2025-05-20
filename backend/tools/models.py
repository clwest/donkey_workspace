from django.db import models


class Tool(models.Model):
    """Represents an executable tool integration."""

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    schema = models.JSONField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True)
    agent_only = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - simple display
        return self.name


class ToolUsageLog(models.Model):
    """Record of a tool invocation by an assistant or agent."""

    STATUS_CHOICES = [
        ("success", "Success"),
        ("error", "Error"),
    ]

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="logs")
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    agent = models.ForeignKey(
        "agents.Agent", on_delete=models.SET_NULL, null=True, blank=True
    )
    input_data = models.JSONField()
    output_data = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple display
        return f"{self.tool.slug} ({self.status})"
