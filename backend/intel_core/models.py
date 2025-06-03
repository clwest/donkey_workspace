from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
import uuid
from django.utils.text import slugify
from prompts.utils.token_helpers import EMBEDDING_MODEL

EMBEDDING_LENGTH = 1536


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(default=uuid.uuid4)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
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
    is_glossary = models.BooleanField(default=False)
    tags = ArrayField(models.CharField(max_length=64), default=list, blank=True)
    fingerprint = models.CharField(max_length=64, unique=True)
    score = models.FloatField(default=1.0)
    glossary_score = models.FloatField(default=0.0)
    matched_anchors = ArrayField(
        models.CharField(max_length=64), default=list, blank=True
    )
    force_embed = models.BooleanField(default=False)
    quality_notes = models.TextField(blank=True)
    anchor = models.ForeignKey(
        "memory.SymbolicMemoryAnchor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chunks",
    )
    embedding = models.OneToOneField(
        "EmbeddingMetadata",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chunk",
    )
    embedding_status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("embedded", "Embedded"),
            ("failed", "Failed"),
            ("skipped", "Skipped"),
        ],
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
    stage = models.CharField(max_length=50, default="queued")
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    current_chunk = models.IntegerField(default=0)
    total_chunks = models.IntegerField(default=0)
    message = models.TextField(blank=True)
    result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job {self.job_id} - {self.status} ({self.progress}%)"


class DocumentProgress(models.Model):
    """Tracks chunking progress for large documents like PDFs."""

    progress_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True)
    total_chunks = models.IntegerField(default=0)
    processed = models.IntegerField(default=0)
    embedded_chunks = models.IntegerField(default=0)
    failed_chunks = ArrayField(models.IntegerField(), default=list, blank=True)
    error_message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if (
            self.status not in {"completed", "failed"}
            and self.total_chunks > 0
            and self.processed >= self.total_chunks
        ):
            self.status = "completed"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.processed}/{self.total_chunks}"


class DocumentSet(models.Model):
    """Group multiple documents for assistant creation."""

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    urls = models.JSONField(blank=True, null=True)
    videos = models.JSONField(blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True)
    documents = models.ManyToManyField(
        Document, related_name="document_sets", blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="document_sets",
    )
    embedding_index = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper

        return self.title


class GlossaryUsageLog(models.Model):
    """Record glossary detection events during RAG retrieval."""

    query = models.TextField()
    rag_used = models.BooleanField(default=False)
    glossary_present = models.BooleanField(default=False)
    retrieval_score = models.FloatField(default=0.0)
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    linked_chunk = models.ForeignKey(
        DocumentChunk,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="glossary_logs",
    )
    reflected_on = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Glossary log for {self.assistant} - used: {self.rag_used}"


class GlossaryMissReflectionLog(models.Model):
    """Store fallback events when glossary context was insufficient."""

    anchor = models.ForeignKey("memory.SymbolicMemoryAnchor", on_delete=models.CASCADE)
    user_question = models.TextField()
    assistant_response = models.TextField()
    matched_chunks = models.ManyToManyField(DocumentChunk)
    glossary_chunk_ids = ArrayField(models.CharField(max_length=64), default=list)
    score_snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    reflection = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class GlossaryFallbackReflectionLog(models.Model):
    """Record when glossary context was ignored or missing."""

    anchor_slug = models.SlugField()
    chunk_id = models.CharField(max_length=64)
    match_score = models.FloatField(default=0.0)
    assistant_response = models.TextField()
    glossary_injected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
