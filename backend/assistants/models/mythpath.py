from django.db import models
from .assistant import Assistant


class MythpathEvent(models.Model):
    assistant = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="mythpath_events"
    )
    event_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    codex_source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"{self.event_type} for {self.assistant.name}"


class TemporalMythpathRecord(models.Model):
    assistant = models.OneToOneField(
        Assistant, on_delete=models.CASCADE, related_name="mythpath_record"
    )
    events = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Mythpath for {self.assistant.name}"


class MythpathSerializationLog(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    record = models.ForeignKey(TemporalMythpathRecord, on_delete=models.CASCADE)
    exported_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"Mythpath export for {self.assistant.name}"
