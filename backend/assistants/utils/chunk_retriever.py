from __future__ import annotations
import logging
from typing import List, Dict, Tuple, Optional
from django.shortcuts import get_object_or_404
from assistants.models.assistant import Assistant
from assistants.models.project import AssistantProject
from intel_core.models import DocumentChunk

# Boost acronym chunks
from intel_core.services import AcronymGlossaryService
from memory.models import SymbolicMemoryAnchor

# Import directly from helpers_io to avoid __init__ fallbacks
from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.vector_utils import compute_similarity

logger = logging.getLogger(__name__)


def get_relevant_chunks(
    assistant_id: Optional[str],
    query_text: str,
    *,
    project_id: Optional[str] = None,
    document_id: Optional[str] = None,
    score_threshold: float = 0.75,
    keywords: Optional[List[str]] = None,
    fallback_min: float = 0.5,
    fallback_limit: int = 2,
) -> Tuple[
    List[Dict[str, object]],
    Optional[str],
    bool,
    bool,
    float,
    Optional[str],
]:
    """Return top matching chunks and an optional ignore reason.

    Results are filtered by ``score_threshold`` and optionally reranked if
    ``keywords`` are provided.  The return value is ``(chunks, reason, fallback,
    glossary_present, top_score, top_chunk_id)`` where ``reason`` is ``"low
    score"`` when matches exist but all fall below the threshold. ``fallback``
    indicates that low-score chunks were returned. ``glossary_present`` is ``True``
    if any candidate chunk contains glossary hints. ``top_score`` and
    ``top_chunk_id`` reflect the best scoring chunk before filtering.
    """
    if not query_text:
        return [], None, False, False, 0.0, None

    logger.info("🔍 Searching document embeddings for query: %s", query_text[:80])

    assistant = None
    if assistant_id:
        assistant = (
            Assistant.objects.filter(id=assistant_id).first()
            or Assistant.objects.filter(slug=assistant_id).first()
        )
        if not assistant:
            logger.warning("Assistant %s not found", assistant_id)
    doc_ids: List[str] = []

    if document_id:
        doc_ids = [document_id]
    elif project_id:
        project = (
            AssistantProject.objects.filter(id=project_id).first()
            or AssistantProject.objects.filter(slug=project_id).first()
        )
        if project:
            doc_ids = list(project.documents.values_list("id", flat=True))
    elif assistant:
        doc_ids = list(assistant.documents.values_list("id", flat=True))
        if assistant.current_project_id:
            doc_ids += list(
                assistant.current_project.documents.values_list("id", flat=True)
            )
    if not doc_ids:
        return [], None, False, False, 0.0, None

    try:
        query_vec = get_embedding_for_text(query_text)
    except Exception as exc:  # pragma: no cover - network
        logger.error("Embedding generation failed: %s", exc)
        return [], None, False, False, 0.0, None
    if not query_vec:
        return [], None, False, False, 0.0, None

    chunks = DocumentChunk.objects.filter(
        document_id__in=doc_ids, embedding__isnull=False
    ).select_related("embedding", "document")
    force_keywords = [
        "opening line",
        "first sentence",
        "beginning of the video",
        "speaker said",
        "quote",
    ]
    force_inject = any(k in query_text.lower() for k in force_keywords)

    scored = []
    glossary_present = False
    query_terms = AcronymGlossaryService.extract(query_text)
    all_anchors = list(SymbolicMemoryAnchor.objects.values_list("slug", flat=True))
    anchor_matches = [s for s in all_anchors if s.lower() in query_text.lower()]
    for chunk in chunks:
        vec = chunk.embedding.vector if chunk.embedding else None
        if vec is None:
            continue
        score = compute_similarity(query_vec, vec)
        if keywords and any(k.lower() in chunk.text.lower() for k in keywords):
            score += 0.05
        contains_glossary = False
        for acro, longform in AcronymGlossaryService.KNOWN.items():
            if (
                acro.lower() in chunk.text.lower()
                and longform.lower() in chunk.text.lower()
            ):
                score += 0.1
                contains_glossary = True
                glossary_present = True
        if chunk.order == 0 and "refers to" in chunk.text.lower():
            score += 0.05
            contains_glossary = True
            glossary_present = True
        if getattr(chunk, "is_glossary", False):
            score += 0.1
            glossary_present = True
        if query_terms and (
            getattr(chunk, "is_glossary", False)
            or "glossary" in getattr(chunk, "tags", [])
        ):
            score += 0.15
        if chunk.anchor and chunk.anchor.slug in anchor_matches:
            score += 0.15
        logger.debug(
            "Retrieved chunk score: %.4f | contains_glossary=%s",
            score,
            contains_glossary,
        )
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0] if scored else 0.0
    top_chunk_id = str(scored[0][1].id) if scored else None
    filtered = [(s, c) for s, c in scored if s >= score_threshold]
    reason = None
    fallback = False

    strong_matches = filtered[:3]
    anchor_pairs = [
        p for p in scored if p[1].anchor and p[1].anchor.slug in anchor_matches
    ]
    if force_inject and scored:
        reason = reason or "forced"
        fallback = True
        pairs = scored[: max(1, fallback_limit)]
    elif strong_matches:
        pairs = strong_matches
    elif scored:
        fallback = True
        reason = "low score"
        logger.warning("\u26a0\ufe0f RAG fallback: using low-score chunks")
        # take top ``fallback_limit`` above ``fallback_min`` if any
        candidates = [p for p in scored if p[0] >= fallback_min] or scored
        pairs = candidates[: max(1, fallback_limit)]
        for i, (s, c) in enumerate(pairs, 1):
            logger.info("Fallback chunk %s score %.4f", i, s)
    else:
        return [], None, False, glossary_present, top_score, top_chunk_id

    # Ensure anchor matched chunks are injected
    for pair in anchor_pairs:
        if pair not in pairs:
            pairs.append(pair)
            reason = reason or "forced anchor"
            fallback = True

    pairs.sort(key=lambda x: x[0], reverse=True)

    result = []
    for score, chunk in pairs:
        result.append(
            {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "score": round(score, 4),
                "text": chunk.text,
                "source_doc": chunk.document.title,
                "is_glossary": getattr(chunk, "is_glossary", False),
                "anchor_slug": getattr(getattr(chunk, "anchor", None), "slug", None),
            }
        )

    return result, reason, fallback, glossary_present, top_score, top_chunk_id


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
