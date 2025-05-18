# embeddings/mixins.py

# from .helpers import save_embedding
from django.db import transaction
import uuid
from django.db import models


class EmbeddingMixin:
    """A mixin to save embeddings for any model."""

    def save(self, *args, **kwargs):
        """
        Override the save method to handle content_id type conversion if needed.
        Convert UUID content_id to string for proper database handling.
        """
        # If content_id is UUID but the referenced model uses integer primary keys,
        # we need to handle the conversion
        if isinstance(self.content_id, uuid.UUID) and self.content_type == "document":
            try:
                # Convert to string for storage to avoid type mismatch
                self.content_id = str(self.content_id)
            except Exception as e:
                print(f"Error converting content_id: {e}")

        super().save(*args, **kwargs)

    def save_embedding(self, content_type, vector):
        from .helpers import save_embedding

        save_embedding(
            content_id=self.id,
            content_type=content_type,
            embedding=vector,
            session_id=self.session_id if hasattr(self, "session_id") else None,
            # might want to change this to read instead of a boolean check
            topic_id=self.topic.id if hasattr(self, "topic") and self.topic else None,
        )
