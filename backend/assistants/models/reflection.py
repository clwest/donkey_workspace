import uuid
from django.db import models

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

    title = models.CharField(max_length=255)
    summary = models.TextField()
    raw_prompt = models.TextField(null=True, blank=True)
    llm_summary = models.TextField(null=True, blank=True)
    insights = models.TextField(null=True, blank=True)
    mood = models.CharField(max_length=50, null=True, blank=True)

    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    related_chunks = models.ManyToManyField(
        "intel_core.DocumentChunk", blank=True, related_name="reflection_logs"
    )
    anchor = models.ForeignKey(
        "memory.SymbolicMemoryAnchor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reflection_logs",
    )
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
