import re
from textstat import textstat
from intel_core.models import Document, DocumentChunk


def is_chunk_clean(text: str) -> bool:
    """Return True if ``text`` passes basic quality checks."""
    if len(text.strip()) < 20:
        return False
    if textstat.flesch_reading_ease(text) < 5:
        return False
    if sum(c.isalnum() for c in text) / max(len(text), 1) < 0.5:
        return False
    words = text.split()
    if words and len(set(words)) / len(words) < 0.3:
        return False
    if re.search(r"(.)\1{4,}", text):
        return False
    return True


def dedupe_document_chunks(document: Document) -> int:
    """Remove duplicate chunks by order, keeping the earliest created."""
    duplicates = 0
    qs = (
        DocumentChunk.objects.filter(document=document)
        .order_by("order", "id")
        .select_related("embedding")
    )
    seen = set()
    for chunk in qs:
        if chunk.order in seen:
            if chunk.embedding:
                chunk.embedding.delete()
            chunk.delete()
            duplicates += 1
        else:
            seen.add(chunk.order)
    return duplicates


def update_document_status(document: Document) -> None:
    """Update ``document.status`` based on embedding progress."""
    total = document.chunks.count()
    if total == 0:
        if document.status != "completed":
            document.status = "failed"
            if not document.progress_error:
                document.progress_error = "no_chunks"
            document.save(update_fields=["status", "progress_error"])
        return

    embedded = document.chunks.filter(embedding_status="embedded").count()
    if embedded == total:
        new_status = "completed"
    elif embedded > 0:
        new_status = "partial"
    else:
        new_status = "processing"
    if document.status != new_status:
        document.status = new_status
        document.save(update_fields=["status"])


def delete_failed_chunks(document: Document) -> int:
    """Delete chunks with embedding_status='failed' for ``document``."""
    failed_qs = document.chunks.filter(embedding_status="failed")
    count = failed_qs.count()
    from intel_core.models import EmbeddingMetadata

    emb_ids = list(failed_qs.values_list("embedding_id", flat=True))
    if emb_ids:
        EmbeddingMetadata.objects.filter(id__in=emb_ids).delete()
    failed_qs.delete()
    return count
