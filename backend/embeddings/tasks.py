"""
Celery tasks for embeddings processing.
"""

import logging
from types import SimpleNamespace

from celery import shared_task

from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.helpers.helpers_io import save_embedding

logger = logging.getLogger("embeddings")


@shared_task(bind=True)
def embed_and_store(
    self,
    text: str,
    content_type: str,
    content_id: str,
    model: str = "text-embedding-3-small",
) -> str:
    """
    Generate an embedding for the given text and store it in the database.

    Args:
        text: The text to embed.
        content_type: Type of content (e.g., 'document', 'chat_message').
        content_id: Identifier of the content.
        model: Embedding model to use.

    Returns:
        The ID of the stored embedding, or None on failure.
    """
    try:
        embedding = generate_embedding(text, model=model)
        if not embedding:
            logger.error(
                f"Embedding generation returned no result for {content_type}:{content_id}"
            )
            return None

        # Prepare a minimal object for saving
        obj = SimpleNamespace(content_type=content_type, id=content_id)
        emb_record = save_embedding(obj, embedding)
        if not emb_record:
            logger.error(f"Failed to save embedding for {content_type}:{content_id}")
            return None

        emb_id = getattr(emb_record, "id", None)
        logger.info(
            f"Successfully embedded and stored {content_type}:{content_id} -> "
            f"embedding_id={emb_id}, size={len(embedding)}"
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
            f"Error in embed_and_store task for {content_type}:{content_id}: {exc}",
            exc_info=True,
        )
        return None
