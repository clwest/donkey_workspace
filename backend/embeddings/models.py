from django.db import models
from pgvector.django import VectorField
import uuid
from embeddings.mixins import EmbeddingMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from story.models import Story
from prompts.utils.token_helpers import EMBEDDING_MODEL

EMBEDDING_LENGTH = 1536


class EmbeddingManager(models.Manager):
    """
    Custom manager for Embedding model to handle UUID/integer type mismatches
    """

    def get_by_natural_key(self, content_type, content_id):
        # Handle potential type mismatch
        if isinstance(content_id, uuid.UUID) and content_type == "document":
            # Try with string content_id first
            return self.get(content_type=content_type, content_id=str(content_id))
        return self.get(content_type=content_type, content_id=content_id)

    def filter_by_content_id(self, content_id, **kwargs):
        """
        Filter embeddings by content_id handling UUID/int conversion
        """
        try:
            # If it's a UUID, also try string representation
            if isinstance(content_id, uuid.UUID):
                return self.filter(content_id=str(content_id), **kwargs)
            return self.filter(content_id=content_id, **kwargs)
        except Exception as e:
            # Log filtering errors and return empty queryset
            import logging

            logger = logging.getLogger("django")
            logger.warning(f"Error in filter_by_content_id: {e}")
            return self.none()


class Embedding(models.Model, EmbeddingMixin):
    CONTENT_TYPES = [
        ("chat_message", "Chat Message"),
        ("document", "Document"),
        ("image", "Image"),
        ("audio", "Audio"),
        ("post", "Post"),
        ("thought", "Assistant Thought"),
        ("reflection", "Assistant Reflection"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,  # TEMPORARY for migration safety
    )
    # Use CharField to accommodate both UUID and integer primary keys
    object_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Primary key of the related object as a string",
    )
    content_object = GenericForeignKey("content_type", "object_id")

    content_id = models.CharField(
        max_length=100,
        help_text="Legacy content ID (related record ID) stored as string",
    )

    content = models.TextField(null=True, blank=True)
    session_id = models.UUIDField(null=True, blank=True)
    source_type = models.CharField(
        max_length=50, null=True, blank=True
    )  # URL, YouTube, Chat, etc.
    embedding = VectorField(dimensions=EMBEDDING_LENGTH, help_text="Vector Embedding")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ Manager
    objects = EmbeddingManager()

    class Meta:
        app_label = "embeddings"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        db_table = "embeddings_embedding"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.content_type} - {self.object_id}"
            if self.content_type
            else "Unknown Embedding"
        )

    @property
    def is_valid_vector(self) -> bool:
        """Return True if the stored vector has non-zero magnitude."""
        vec = self.embedding or []
        return bool(vec) and any(abs(v) > 0 for v in vec)


class TagConcept(models.Model):
    """Predefined semantic tags with their embeddings for inference."""

    name = models.CharField(max_length=100, unique=True)
    embedding = VectorField(
        dimensions=EMBEDDING_LENGTH, help_text="Embedding vector for the semantic tag"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StoryChunkEmbedding(models.Model):
    """Stores embeddings and inferred tags for each paragraph/chunk of a story."""

    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name="chunk_embeddings"
    )
    paragraph_index = models.PositiveIntegerField()
    text = models.TextField()
    embedding = VectorField(
        dimensions=EMBEDDING_LENGTH, help_text="Embedding vector for this text chunk"
    )
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "embeddings"
        unique_together = ("story", "paragraph_index")
        ordering = ["paragraph_index"]

    def __str__(self):
        return f"Chunk {self.paragraph_index} of Story {self.story_id}"


class EmbeddingDebugTag(models.Model):
    """Tag embeddings during audits for developer review."""

    embedding = models.ForeignKey(
        Embedding, on_delete=models.CASCADE, related_name="debug_tags"
    )
    reason = models.TextField()
    repair_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "pending"),
            ("repaired", "repaired"),
            ("failed", "failed"),
            ("skipped", "skipped"),
            ("ignored", "ignored"),
        ],
        default="pending",
    )
    repair_attempts = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    repaired_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "embeddings"
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - simple helper
        return f"{self.embedding_id} {self.reason} [{self.repair_status}]"


class EmbeddingDriftLog(models.Model):
    """Historical record of embedding drift counts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=100)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="embedding_drift_logs",
    )
    context = models.ForeignKey(
        "mcp_core.MemoryContext",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="embedding_drift_logs",
    )
    mismatched_count = models.PositiveIntegerField()
    orphaned_count = models.PositiveIntegerField()
    repaired_count = models.PositiveIntegerField()
    repair_attempted_at = models.DateTimeField(null=True, blank=True)
    repair_success_count = models.PositiveIntegerField(default=0)
    repair_failure_count = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "embeddings"
        ordering = ["-timestamp"]

    def __str__(self):  # pragma: no cover - simple display
        return f"{self.model_name} {self.mismatched_count}/{self.orphaned_count}"


class EmbeddingRepairLog(models.Model):
    """Record metadata or quality repair actions for an embedding."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    embedding = models.ForeignKey(
        Embedding, on_delete=models.CASCADE, related_name="repair_logs"
    )
    action = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "embeddings"
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - simple helper
        return f"{self.embedding_id} {self.action}"
