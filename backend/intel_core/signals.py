"""Deprecated signal hooks for search vector updates."""

# These functions previously managed a ``search_vector`` field on
# ``Document`` instances via ``pre_save`` and ``post_save`` signals.
# The ``Document`` model no longer includes that field, so the signal
# handlers have been removed.  This module remains to avoid import
# errors from any legacy code.


def update_document_search_vector(sender, instance, **kwargs):
    """Deprecated stub kept for backward compatibility."""
    pass


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from memory.models import MemoryEntry
from mcp_core.models import MemoryContext
from assistants.models.assistant import Assistant
from .models import DocumentChunk, EmbeddingMetadata, DocumentProgress
from embeddings.models import Embedding
from embeddings.helpers.helpers_io import save_embedding
from prompts.utils.token_helpers import EMBEDDING_MODEL
import logging


@receiver(post_save, sender=DocumentChunk)
def create_memory_from_chunk(sender, instance, created, **kwargs):
    if not created:
        return

    assistants = list(instance.document.linked_assistants.all())
    if not assistants:
        MemoryEntry.objects.create(
            event=instance.text[:200],
            summary=instance.text[:200],
            document=instance.document,
            linked_content_type=ContentType.objects.get_for_model(DocumentChunk),
            linked_object_id=instance.id,
            type="document_chunk",
        )
        return

    for assistant in assistants:
        context = MemoryContext.objects.create(
            target_content_type=ContentType.objects.get_for_model(Assistant),
            target_object_id=assistant.id,
            content=instance.text[:200],
        )
        MemoryEntry.objects.create(
            event=instance.text[:200],
            summary=instance.text[:200],
            document=instance.document,
            linked_content_type=ContentType.objects.get_for_model(DocumentChunk),
            linked_object_id=instance.id,
            type="document_chunk",
            assistant=assistant,
            context=context,
        )


@receiver(post_save, sender=Embedding)
def link_embedding_metadata(sender, instance, created, **kwargs):
    """Create EmbeddingMetadata and link to DocumentChunk when embedding saved."""
    if not created:
        return

    logger = logging.getLogger("intel_core")
    try:
        if not instance.content_type or instance.content_type.model != "documentchunk":
            return
        chunk = DocumentChunk.objects.filter(id=instance.object_id).first()
        if not chunk or chunk.embedding_id:
            return
        vector = list(instance.embedding) if instance.embedding is not None else []
        meta = EmbeddingMetadata.objects.create(
            model_used=EMBEDDING_MODEL,
            num_tokens=getattr(chunk, "tokens", 0),
            vector=vector,
            status="completed",
            source=getattr(chunk.document, "source_type", ""),
        )
        chunk.embedding = meta
        chunk.embedding_status = "embedded"
        chunk.save(update_fields=["embedding", "embedding_status"])

        mem_qs = MemoryEntry.objects.filter(
            linked_content_type=ContentType.objects.get_for_model(DocumentChunk),
            linked_object_id=chunk.id,
        )
        for mem in mem_qs:
            if not mem.embeddings.exists():
                save_embedding(mem, vector)

        progress_id = None
        if isinstance(chunk.document.metadata, dict):
            progress_id = chunk.document.metadata.get("progress_id")

        prog = None
        if progress_id:
            prog = DocumentProgress.objects.filter(progress_id=progress_id).first()

        if not prog:
            total = chunk.document.chunks.count()
            embedded = chunk.document.chunks.filter(embedding__isnull=False).count()
            prog = DocumentProgress.objects.create(
                title=chunk.document.title,
                total_chunks=total,
                processed=total,
                embedded_chunks=embedded,
                status="pending",
            )
            metadata = chunk.document.metadata or {}
            metadata["progress_id"] = str(prog.progress_id)
            chunk.document.metadata = metadata
            chunk.document.save(update_fields=["metadata"])

        DocumentProgress.objects.filter(progress_id=prog.progress_id).update(
            embedded_chunks=F("embedded_chunks") + 1
        )
        prog.refresh_from_db()
        if (
            prog.status != "failed"
            and prog.total_chunks > 0
            and prog.embedded_chunks >= prog.total_chunks
        ):
            prog.status = "completed"
            prog.save(update_fields=["status"])
    except Exception as e:
        logger.warning(f"Failed linking embedding to chunk: {e}")


@receiver(post_save, sender=EmbeddingMetadata)
def update_chunk_status(sender, instance, **kwargs):
    """Ensure DocumentChunk records reflect embedding completion."""
    chunk = getattr(instance, "chunk", None)
    if chunk and chunk.embedding_status != DocumentChunk.EmbeddingStatus.EMBEDDED:
        chunk.embedding_status = DocumentChunk.EmbeddingStatus.EMBEDDED
        chunk.save(update_fields=["embedding_status"])
