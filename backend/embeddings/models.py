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
    object_id = models.UUIDField(null=True, blank=True)  # assuming most use UUID
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
