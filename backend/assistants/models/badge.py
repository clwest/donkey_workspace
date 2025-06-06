from django.db import models


class Badge(models.Model):
    """Skill or reputation badge metadata."""

    slug = models.SlugField(unique=True)
    label = models.CharField(max_length=100)
    emoji = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True)
    criteria = models.TextField(blank=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.label
