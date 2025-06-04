import logging
from django.db.models import Q
from intel_core.models import DocumentChunk
from embeddings.tasks import embed_and_store

logger = logging.getLogger(__name__)


def reembed_missing_chunks() -> dict:
    """Recalculate embeddings for chunks missing vectors or scores."""
    chunks = DocumentChunk.objects.filter(
        Q(embedding__isnull=True) | Q(embedding__vector__isnull=True) | Q(glossary_score=0)
    ).select_related("embedding")
    ids = []
    tokens = 0
    for ch in chunks:
        embed_and_store.delay(str(ch.id))
        ids.append(str(ch.id))
        tokens += getattr(ch, "tokens", 0)
    logger.info("Reembedding %d chunks", len(ids))
    return {"reprocessed": ids, "total_tokens": tokens}
