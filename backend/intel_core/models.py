from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
import uuid
from django.utils.text import slugify

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_LENGTH = 1536


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=120)
    description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    # Allow source_url to be optional for locally uploaded documents
    source_url = models.URLField(blank=True, null=True)
    summary = models.TextField(null=True, blank=True)  # ✅ Add this
    SOURCE_TYPE_CHOICES = [
        ("url", "URL"),
        ("pdf", "PDF"),
        ("youtube", "YouTube"),
        ("markdown", "Markdown"),
        ("text", "Plain Text"),
    ]

    source_type = models.CharField(
        max_length=20, choices=SOURCE_TYPE_CHOICES, default="url"
    )
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    duration = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField(
        "mcp_core.Tag", blank=True, related_name="document_tags"
    )
    ingested_by = models.CharField(max_length=128, blank=True, null=True)
    token_count_int = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[
                :50
            ]  # Ensure it's under VARCHAR(50) if limited
        super().save(*args, **kwargs)


class DocumentInteraction(models.Model):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="interactions"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.document.title}"


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="chunks"
    )
    order = models.PositiveIntegerField()
    text = models.TextField()
    tokens = models.IntegerField()
    chunk_type = models.CharField(max_length=30, default="body")
    fingerprint = models.CharField(max_length=64, unique=True)
    embedding = models.OneToOneField(
        "EmbeddingMetadata",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chunk",
    )

    def __str__(self):
        return f"Chunk {self.order} of {self.document.title}"


class DocumentFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="favorites"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "document")


class ChunkTag(models.Model):
    chunk = models.ForeignKey(
        DocumentChunk, on_delete=models.CASCADE, related_name="chunk_tags"
    )
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EmbeddingMetadata(models.Model):
    embedding_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    model_used = models.CharField(max_length=100)
    num_tokens = models.IntegerField()
    vector = ArrayField(models.FloatField())
    status = models.CharField(max_length=20, default="pending")
    source = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model_used} | {self.embedding_id}"


class JobStatus(models.Model):
    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=50)
    progress = models.IntegerField(default=0)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job {self.job_id} - {self.status} ({self.progress}%)"
