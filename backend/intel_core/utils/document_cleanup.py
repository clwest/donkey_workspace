from intel_core.models import Document, DocumentChunk


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
    """Update ``document.status`` when all chunks have embeddings."""
    total = document.chunks.count()
    if total == 0:
        return
    embedded = document.chunks.filter(embedding_status="embedded").count()
    new_status = "completed" if embedded == total else "pending"
    if document.status != new_status:
        document.status = new_status
        document.save(update_fields=["status"])
