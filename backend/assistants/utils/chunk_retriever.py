from __future__ import annotations
import logging
from typing import List, Dict, Tuple, Optional
from django.shortcuts import get_object_or_404
from assistants.models.assistant import Assistant
from intel_core.models import DocumentChunk
# Import directly from helpers_io to avoid __init__ fallbacks
from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.vector_utils import compute_similarity

logger = logging.getLogger(__name__)


def get_relevant_chunks(
    assistant_id: str,
    query_text: str,
    *,
    score_threshold: float = 0.75,
    keywords: Optional[List[str]] = None,
    fallback_min: float = 0.5,
    fallback_limit: int = 2,
) -> Tuple[List[Dict[str, object]], Optional[str], bool]:
    """Return top matching chunks and an optional ignore reason.

    Results are filtered by ``score_threshold`` and optionally reranked if
    ``keywords`` are provided.  The return value is ``(chunks, reason, fallback)``
    where ``reason`` is ``"low score"`` when matches exist but all fall below the
    threshold. ``fallback`` indicates that low-score chunks were returned.
    """
    if not query_text:
        return [], None, False

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
        return [], None, False

    doc_ids = list(assistant.documents.values_list("id", flat=True))
    if assistant.current_project_id:
        doc_ids += list(
            assistant.current_project.documents.values_list("id", flat=True)
        )
    if not doc_ids:
        return [], None, False

    try:
        query_vec = get_embedding_for_text(query_text)
    except Exception as exc:  # pragma: no cover - network
        logger.error("Embedding generation failed: %s", exc)
        return [], None, False
    if not query_vec:
        return [], None, False

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
        if keywords and any(k.lower() in chunk.text.lower() for k in keywords):
            score += 0.05
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    filtered = [(s, c) for s, c in scored if s >= score_threshold]
    reason = None
    fallback = False

    pairs = filtered[:3]
    if not pairs and scored:
        fallback = True
        reason = "low score"
        logger.warning("\u26a0\ufe0f RAG fallback: using low-score chunks")
        # take top ``fallback_limit`` above ``fallback_min`` if any
        candidates = [p for p in scored if p[0] >= fallback_min]
        if not candidates:
            candidates = scored
        pairs = candidates[:fallback_limit]

    result = []
    for score, chunk in pairs:
        result.append(
            {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "score": round(score, 4),
                "text": chunk.text,
                "source_doc": chunk.document.title,
            }
        )

    return result, reason, fallback


def format_chunks(chunks: List[Dict[str, object]]) -> str:
    """Return a user-facing block for LLM prompting."""
    if not chunks:
        return ""
    lines = ["MEMORY CHUNKS", "=================="]
    for i, info in enumerate(chunks, 1):
        text = info.get("text", "").strip()
        lines.append(f"[{i}] {text}")
    lines.append("==================")
    return "\n".join(lines)
