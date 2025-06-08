from django.db import models
from django.utils import timezone


class DemoSessionLog(models.Model):
    """Track anonymous demo assistant usage sessions."""

    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="demo_logs",
    )
    session_id = models.CharField(max_length=64, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    message_count = models.IntegerField(default=0)
    demo_interaction_score = models.IntegerField(default=0)
    starter_query = models.TextField(blank=True)
    first_message = models.TextField(blank=True)
    first_message_score = models.FloatField(null=True, blank=True)
    converted_to_real_assistant = models.BooleanField(default=False)
    likely_to_convert = models.BooleanField(default=False)
    tips_helpful = models.IntegerField(default=0)
    created_from_ip = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.assistant} | {self.session_id}"
