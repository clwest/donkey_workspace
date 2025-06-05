import logging
from typing import Iterable, List

from intel_core.models import DocumentChunk

logger = logging.getLogger(__name__)


def fetch_chunks(
    doc_ids: Iterable[str] | None = None,
    *,
    chunk_ids: Iterable[str] | None = None,
    repair: bool = False,
) -> List[DocumentChunk]:
    """Return chunks for the given documents or IDs respecting ``embedding_status``."""
    qs = DocumentChunk.objects.filter(embedding__isnull=False)
    if doc_ids is not None:
        qs = qs.filter(document_id__in=doc_ids)
    if chunk_ids is not None:
        qs = qs.filter(id__in=chunk_ids)
    qs = qs.select_related("embedding", "document").order_by("order")
    results = []
    for chunk in qs:
        if chunk.embedding_status == DocumentChunk.EmbeddingStatus.EMBEDDED:
            results.append(chunk)
            continue
        if repair and chunk.embedding and chunk.embedding.status == "completed":
            logger.warning(
                "Chunk %s has status %s but embedding exists; including due to repair",
                chunk.id,
                chunk.embedding_status,
            )
            results.append(chunk)
        else:
            logger.debug(
                "Skipping chunk %s with status %s", chunk.id, chunk.embedding_status
            )
    return results
