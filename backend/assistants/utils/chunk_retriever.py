from __future__ import annotations
import logging
from typing import List
from django.shortcuts import get_object_or_404
from assistants.models.assistant import Assistant
from intel_core.models import DocumentChunk
# Import directly from helpers_io to avoid __init__ fallbacks
from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.vector_utils import compute_similarity

logger = logging.getLogger(__name__)


def get_relevant_chunks(assistant_id: str, query_text: str) -> List[str]:
    """Return up to three document chunks most similar to ``query_text``.

    The search is limited to documents linked to the assistant or its current
    project.  Results are ordered by vector similarity.
    """
    if not query_text:
        return []

    logger.info(
        "🔍 Searching document embeddings for assistant %s with query: %s",
        assistant_id,
        query_text[:80],
    )

    assistant = (
        Assistant.objects.filter(id=assistant_id).first()
        or Assistant.objects.filter(slug=assistant_id).first()
    )
    if not assistant:
        logger.warning("Assistant %s not found", assistant_id)
        return []

    doc_ids = list(assistant.documents.values_list("id", flat=True))
    if assistant.current_project_id:
        doc_ids += list(
            assistant.current_project.documents.values_list("id", flat=True)
        )
    if not doc_ids:
        return []

    try:
        query_vec = get_embedding_for_text(query_text)
    except Exception as exc:  # pragma: no cover - network
        logger.error("Embedding generation failed: %s", exc)
        return []
    if not query_vec:
        return []

    chunks = (
        DocumentChunk.objects.filter(document_id__in=doc_ids, embedding__isnull=False)
        .select_related("embedding", "document")
    )
    scored = []
    for chunk in chunks:
        vec = chunk.embedding.vector if chunk.embedding else None
        if vec is None:
            continue
        score = compute_similarity(query_vec, vec)
        scored.append((score, chunk.text))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored[:3]]
