from django.db import models
from assistants.models.assistant import Assistant


class CodexInheritanceLink(models.Model):
    mentor = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="codex_children"
    )
    child = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="codex_parents"
    )
    inherited_clauses = models.JSONField(default=list, blank=True)
    mutated_clauses = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.mentor.name} -> {self.child.name}"


class CodexLineageThread(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    lineage_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Lineage thread for {self.assistant.name}"
