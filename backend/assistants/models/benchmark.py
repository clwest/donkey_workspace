import uuid
from django.db import models


class AssistantTaskRunLog(models.Model):
    """Record each assistant task execution."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="task_runs"
    )
    task_text = models.TextField()
    result_text = models.TextField()
    success = models.BooleanField(default=True)
    reflection = models.ForeignKey(
        "assistants.AssistantReflectionLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_runs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover - simple display helper
        return f"{self.assistant.name} run {self.created_at:%Y-%m-%d}"


class TokenUsageSummary(models.Model):
    """Token usage for a single task run."""

    run_log = models.OneToOneField(
        AssistantTaskRunLog, on_delete=models.CASCADE, related_name="token_summary"
    )
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    def __str__(self):  # pragma: no cover - simple display helper
        return f"Tokens {self.total_tokens} for {self.run_log_id}"


class TaskRetryAuditLog(models.Model):
    """Audit retries of a task run."""

    run_log = models.ForeignKey(
        AssistantTaskRunLog, on_delete=models.CASCADE, related_name="retries"
    )
    reason = models.CharField(max_length=255, blank=True)
    previous_output = models.TextField(blank=True)
    new_output = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover - simple display helper
        return f"Retry of {self.run_log_id}"


class BenchmarkTaskReport(models.Model):
    """Aggregated benchmark stats for repeated tasks."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="benchmarks"
    )
    task_name = models.CharField(max_length=255)
    run_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    avg_tokens = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["assistant", "task_name"]

    def __str__(self):  # pragma: no cover - simple display helper
        return f"Benchmark {self.task_name} ({self.run_count})"
