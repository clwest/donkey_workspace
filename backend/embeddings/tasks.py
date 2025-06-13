"""
Celery tasks for embeddings processing.
"""

from utils.logging_utils import get_logger
from types import SimpleNamespace
import os

from embeddings.utils.chunk_retriever import should_embed_chunk

from celery import shared_task
import traceback

from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.helpers.helpers_io import save_embedding
from prompts.utils.token_helpers import EMBEDDING_MODEL
from django.db.models import F
from intel_core.utils.document_progress import repair_progress


EMBEDDING_LENGTH = 1536

logger = get_logger("embeddings")


@shared_task
def verify_chunk_embedding(chunk_id: str) -> bool:
    """Ensure the chunk's embedding exists and status reflects reality."""
    from intel_core.models import DocumentChunk

    chunk = (
        DocumentChunk.objects.filter(id=chunk_id).select_related("embedding").first()
    )
    if not chunk:
        return False
    has_vector = getattr(chunk.embedding, "vector", None)
    if has_vector and chunk.embedding_status != "embedded":
        chunk.embedding_status = "embedded"
        chunk.save(update_fields=["embedding_status"])
        return True
    if not has_vector and chunk.embedding_status == "embedded":
        chunk.embedding_status = "pending"
        chunk.save(update_fields=["embedding_status"])
        return False
    return bool(has_vector)


@shared_task
def validate_embedded_chunks(limit: int = 100) -> int:
    """Recheck a batch of chunks flagged as embedded."""
    from intel_core.models import DocumentChunk

    checked = 0
    for chunk in DocumentChunk.objects.filter(embedding_status="embedded")[:limit]:
        verify_chunk_embedding(chunk.id)
        checked += 1
    return checked


@shared_task(bind=True)
def embed_and_store(
    self,
    text_or_id: str,
    content_type: str | None = None,
    content_id: str | None = None,
    model: str = EMBEDDING_MODEL,
    session_id: str | None = None,
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
            if not chunk.text:
                logger.warning(
                    f"Skipping embed_and_store for chunk {chunk.id} -- empty text"
                )
                chunk.embedding_status = "skipped"
                chunk.save(update_fields=["embedding_status"])
                return None
            should = should_embed_chunk(chunk)
            if not should:
                logger.info(
                    "[Chunk Skipped] Chunk %s - score=%.3f",
                    chunk.id,
                    chunk.score,
                )
                chunk.embedding_status = "skipped"
                chunk.save(update_fields=["embedding_status"])
                return None
            if chunk.force_embed:
                logger.info(
                    f"⚡️ Force-embedding chunk {chunk.id} despite score={chunk.score}"
                )
            session_id = session_id or str(getattr(chunk.document, "session_id", ""))
            text = chunk.text
            content_type = "document_chunk"
            content_id = str(chunk.id)
        else:
            text = text_or_id
            if content_type == "document_chunk" and content_id:
                from intel_core.models import DocumentChunk

                chunk = DocumentChunk.objects.filter(id=content_id).first()
                if chunk:
                    if not chunk.text:
                        logger.warning(
                            f"Skipping embed_and_store for chunk {chunk.id} -- empty text"
                        )
                        chunk.embedding_status = "skipped"
                        chunk.save(update_fields=["embedding_status"])
                        return None
                    session_id = session_id or str(
                        getattr(chunk.document, "session_id", "")
                    )
                    should = should_embed_chunk(chunk)
                    if not should:
                        logger.info(
                            "[Chunk Skipped] Chunk %s - score=%.3f",
                            chunk.id,
                            chunk.score,
                        )
                        chunk.embedding_status = "skipped"
                        chunk.save(update_fields=["embedding_status"])
                        return None
                    if chunk.force_embed:
                        logger.info(
                            f"⚡️ Force-embedding chunk {chunk.id} despite score={chunk.score}"
                        )

        embedding = generate_embedding(text, model=model)
        if not embedding:
            logger.error(
                f"Embedding generation returned no result for {content_type}:{content_id}"
            )
            if content_type == "document_chunk" and content_id:
                from intel_core.models import DocumentChunk

                DocumentChunk.objects.filter(id=content_id).update(
                    embedding_status="failed"
                )
                logger.info(
                    "[Chunk Failed] Chunk %s - reason: empty_embedding",
                    content_id,
                )
            return None
        if not isinstance(embedding, list) or len(embedding) != 1536:
            logger.warning(
                f"Skipping embed_and_store for {content_type}:{content_id} -- "
                f"invalid vector size {len(embedding) if isinstance(embedding, list) else 'N/A'}"
            )
            if content_type == "document_chunk":
                logger.info(
                    "[Chunk Skipped] Chunk %s - reason: invalid_vector_size",
                    content_id,
                )
                from intel_core.models import DocumentChunk

                DocumentChunk.objects.filter(id=content_id).update(
                    embedding_status="skipped"
                )
            return None

        # Prepare a minimal object for saving
        obj = SimpleNamespace(
            content_type=content_type,
            id=content_id,
            content=text,
        )
        emb_record = save_embedding(obj, embedding, session_id=session_id)
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
            from django.utils import timezone
            from intel_core.models import (
                DocumentChunk,
                Document,
                EmbeddingMetadata,
                DocumentProgress,
            )
            from prompts.utils.token_helpers import count_tokens

            meta = EmbeddingMetadata.objects.filter(id=emb_id).first()
            chunk = (
                DocumentChunk.objects.filter(id=content_id)
                .select_related("document")
                .first()
            )
            if chunk:
                chunk.embedding = meta
                chunk.embedding_status = "embedded"
                chunk.save(update_fields=["embedding", "embedding_status"])

                doc = chunk.document
                embedded = doc.chunks.filter(embedding__isnull=False).count()
                total = doc.chunks.count()
                meta_data = doc.metadata or {}
                meta_data["embedded_chunks"] = embedded
                meta_data.setdefault("chunk_count", total)
                if not doc.token_count_int:
                    doc.token_count_int = count_tokens(doc.content)
                    meta_data["token_count"] = doc.token_count_int
                doc.metadata = meta_data
                doc.updated_at = timezone.now()
                doc.save(update_fields=["metadata", "token_count_int", "updated_at"])
                try:
                    from intel_core.tasks import update_upload_progress

                    update_upload_progress.delay(str(doc.id))
                except Exception as e:  # pragma: no cover - best effort
                    logger.warning(f"update_upload_progress failed: {e}")

                progress_id = None
                if isinstance(doc.metadata, dict):
                    progress_id = doc.metadata.get("progress_id")
                if progress_id:
                    qs = DocumentProgress.objects.filter(progress_id=progress_id)
                    if qs.exists():
                        qs.update(embedded_chunks=F("embedded_chunks") + 1)
                        prog = qs.first()
                        if (
                            prog.status != "failed"
                            and prog.total_chunks > 0
                            and prog.embedded_chunks >= prog.total_chunks
                        ):
                            prog.status = "completed"
                            prog.save(update_fields=["status"])
                        try:
                            repair_progress(document=doc)
                            doc.sync_progress()
                        except Exception as e:  # pragma: no cover - best effort
                            logger.warning(f"repair-progress failed: {e}")
        # Trigger post-processing for character embeddings
        if content_type == "CharacterProfile":
            try:
                from characters.tasks import post_embedding_update

                post_embedding_update.delay(content_id, self.request.id)
            except Exception as e:
                logger.error(
                    f"Failed to schedule post_embedding_update: {e}", exc_info=True
                )
        verify_chunk_embedding.delay(str(content_id))
        return str(emb_id)
    except Exception as exc:
        logger.error(
            f"Embedding failure for chunk {content_id}: {exc}",
            exc_info=True,
        )
        if content_type == "document_chunk":
            from intel_core.models import DocumentChunk

            chunk = DocumentChunk.objects.filter(id=content_id).first()
            if chunk:
                chunk.embedding_status = "failed"
                chunk.save(update_fields=["embedding_status"])
                try:
                    repair_progress(document_id=str(chunk.document_id))
                    chunk.document.sync_progress()
                except Exception as e:  # pragma: no cover - best effort
                    logger.warning(f"repair-progress failed: {e}")
        return None
