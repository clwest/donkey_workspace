import logging
from typing import Iterable, List

from intel_core.models import DocumentChunk

logger = logging.getLogger(__name__)


def fetch_chunks(doc_ids: Iterable[str], repair: bool = False) -> List[DocumentChunk]:
    """Return chunks for the given documents respecting ``embedding_status``."""
    qs = (
        DocumentChunk.objects.filter(document_id__in=doc_ids, embedding__isnull=False)
        .select_related("embedding", "document")
        .order_by("order")
    )
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
