import uuid
from django.db import models

from assistants.models.assistant import Assistant


class TaskAssignment(models.Model):
    """Simple task assignment from one assistant to another."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name="task_assignments_made",
    )
    to_assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name="task_assignments_received",
    )
    description = models.TextField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.from_assistant} -> {self.to_assistant}: {self.description[:20]}"

class AssistantExecutionChain(models.Model):
    """Sequence of assistants, prompts and tools for chained execution."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="execution_chains"
    )
    handoff_criteria = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.title


class ChainNodeMap(models.Model):
    """Map each node in an AssistantExecutionChain."""

    chain = models.ForeignKey(
        AssistantExecutionChain, on_delete=models.CASCADE, related_name="nodes"
    )
    step_order = models.PositiveIntegerField()
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    prompt = models.ForeignKey(
        "prompts.Prompt", on_delete=models.SET_NULL, null=True, blank=True
    )
    tool = models.ForeignKey(
        "tools.Tool", on_delete=models.SET_NULL, null=True, blank=True
    )
    next_on_success = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="prev_success"
    )
    next_on_error = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="prev_error"
    )

    class Meta:
        ordering = ["step_order"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.chain.title} step {self.step_order}"

