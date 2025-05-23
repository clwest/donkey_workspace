from django.db import models


class CinemythStoryline(models.Model):
    """High-level storyline used for mythcasting streams."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class MythcastingChannel(models.Model):
    channel_name = models.CharField(max_length=150)
    active_storyline = models.ForeignKey(CinemythStoryline, on_delete=models.CASCADE)
    viewing_audience = models.JSONField()
    symbolic_broadcast_tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.channel_name


class AudienceFeedbackLoop(models.Model):
    channel = models.ForeignKey(MythcastingChannel, on_delete=models.CASCADE)
    symbolic_trigger = models.CharField(max_length=100)
    feedback_pattern = models.JSONField()
    codex_alignment_shift = models.FloatField()
    assistant_response_vector = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.channel.channel_name} - {self.symbolic_trigger}"


class ParticipatoryStreamEvent(models.Model):
    initiating_viewer_id = models.CharField(max_length=150)
    linked_channel = models.ForeignKey(MythcastingChannel, on_delete=models.CASCADE)
    symbolic_input = models.TextField()
    mythflow_result = models.TextField()
    codex_modified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Event by {self.initiating_viewer_id}"
