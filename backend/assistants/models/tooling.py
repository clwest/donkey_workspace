from django.db import models
from django.conf import settings
from assistants.models.assistant import Assistant
from mcp_core.models import Tag
from .reflection import AssistantReflectionLog


class AssistantTool(models.Model):
    """Tool available specifically to an assistant."""

    assistant = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="custom_tools"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("assistant", "slug")

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.assistant.slug}:{self.slug}"


class AssistantToolAssignment(models.Model):
    """Record of a tool assigned to an assistant."""

    assistant = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="tool_assignments"
    )
    tool = models.ForeignKey(
        AssistantTool, on_delete=models.CASCADE, related_name="assignments"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    reason = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    reflection_log = models.ForeignKey(
        AssistantReflectionLog,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tool_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("assistant", "tool")

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.assistant.slug}->{self.tool.slug}"
