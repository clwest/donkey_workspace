from django.db import models


class AssistantDiagnosticReport(models.Model):
    """Aggregated RAG diagnostic metrics for an assistant."""

    assistant = models.ForeignKey("Assistant", on_delete=models.CASCADE)
    slug = models.SlugField()
    generated_at = models.DateTimeField(auto_now_add=True)
    fallback_rate = models.FloatField()
    glossary_success_rate = models.FloatField()
    avg_chunk_score = models.FloatField()
    rag_logs_count = models.IntegerField()
    summary_markdown = models.TextField(blank=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant.slug} report {self.generated_at.date()}"
