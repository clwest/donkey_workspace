from django.db import models
from django.conf import settings


class FeedbackEntry(models.Model):
    CATEGORY_CHOICES = [
        ("bug", "Bug"),
        ("idea", "Idea"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    assistant_slug = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant_slug} - {self.category}"
