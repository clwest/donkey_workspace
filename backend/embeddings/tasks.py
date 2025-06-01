"""
Celery tasks for embeddings processing.
"""

from utils.logging_utils import get_logger
from types import SimpleNamespace

from celery import shared_task
import traceback

from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.helpers.helpers_io import save_embedding
from prompts.utils.token_helpers import EMBEDDING_MODEL

EMBEDDING_LENGTH = 1536

logger = get_logger("embeddings")


@shared_task(bind=True)
def embed_and_store(
    self,
    text_or_id: str,
    content_type: str | None = None,
    content_id: str | None = None,
    model: str = EMBEDDING_MODEL,
) -> str | None:
    """
    Generate an embedding for the given text and store it in the database.

    Args:
        text_or_id: The text to embed, or a DocumentChunk ID when ``content_type``
            and ``content_id`` are omitted.
        content_type: Type of content (e.g., "document_chunk").
        content_id: Identifier of the content. Optional if ``text_or_id`` is a
            chunk ID.
        model: Embedding model to use.

    Returns:
        The ID of the stored embedding, or None on failure.
    """
    try:
        if content_type is None and content_id is None:
            # ``text_or_id`` is actually a DocumentChunk ID
            from intel_core.models import DocumentChunk

            chunk = DocumentChunk.objects.filter(id=text_or_id).first()
            if not chunk:
                logger.error(f"No DocumentChunk found with id {text_or_id}")
                return None
            text = chunk.text
            content_type = "document_chunk"
            content_id = str(chunk.id)
        else:
            text = text_or_id

        embedding = generate_embedding(text, model=model)
        if not embedding:
            logger.error(
                f"Embedding generation returned no result for {content_type}:{content_id}"
            )
            return None
        if not isinstance(embedding, list) or len(embedding) != 1536:
            logger.warning(
                f"Skipping embed_and_store for {content_type}:{content_id} -- "
                f"invalid vector size {len(embedding) if isinstance(embedding, list) else 'N/A'}"
            )
            return None

        # Prepare a minimal object for saving
        obj = SimpleNamespace(content_type=content_type, id=content_id)
        emb_record = save_embedding(obj, embedding)
        if not emb_record:
            logger.error(f"Failed to save embedding for {content_type}:{content_id}")
            if content_type == "document_chunk":
                from intel_core.models import DocumentChunk

                DocumentChunk.objects.filter(id=content_id).update(
                    embedding_status="failed"
                )
            return None

        emb_id = getattr(emb_record, "id", None)
        logger.info(
            f"Successfully embedded and stored {content_type}:{content_id} -> "
            f"embedding_id={emb_id}, size={len(embedding)}"
        )
        if content_type == "document_chunk":
            from intel_core.models import DocumentChunk, EmbeddingMetadata

            meta = EmbeddingMetadata.objects.filter(embedding_id=emb_id).first()
            DocumentChunk.objects.filter(id=content_id).update(
                embedding=meta, embedding_status="embedded"
            )
        # Trigger post-processing for character embeddings
        if content_type == "CharacterProfile":
            try:
                from characters.tasks import post_embedding_update

                post_embedding_update.delay(content_id, self.request.id)
            except Exception as e:
                logger.error(
                    f"Failed to schedule post_embedding_update: {e}", exc_info=True
                )
        return str(emb_id)
    except Exception as exc:
        logger.error(
            f"Embedding failure for chunk {content_id}: {exc}",
            exc_info=True,
        )
        if content_type == "document_chunk":
            from intel_core.models import DocumentChunk

            DocumentChunk.objects.filter(id=content_id).update(
                embedding_status="failed"
            )
        return None
