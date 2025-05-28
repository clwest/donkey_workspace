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
from django.conf import settings

# Minimum score required to bypass normal filtering when forcing
# glossary chunks for an anchor match
GLOSSARY_MIN_SCORE_OVERRIDE = 0.15
# Minimum similarity score for a chunk to be considered at all.
MIN_SCORE = 0.05

# Score boost applied when a chunk's anchor matches the query.
ANCHOR_BOOST = getattr(settings, "RAG_ANCHOR_BOOST", 0.1)

logger = logging.getLogger(__name__)


def _anchor_in_query(anchor: SymbolicMemoryAnchor, text: str) -> bool:
    """Return True if ``text`` mentions ``anchor`` via slug, label or tags."""
    q = text.lower()
    if anchor.slug.lower() in q or anchor.label.lower() in q:
        return True
    if anchor.tags.filter(slug__in=q.split()).exists():
        return True
    if anchor.tags.filter(name__in=q.split()).exists():
        return True
    return False


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
    auto_expand: bool = False,
) -> Tuple[
    List[Dict[str, object]],
    Optional[str],
    bool,
    bool,
    float,
    Optional[str],
    bool,
    bool,
]:
    """Return top matching chunks and an optional ignore reason.

    Results are filtered by ``score_threshold`` and optionally reranked if
    ``keywords`` are provided.  The return value is ``(chunks, reason, fallback,
    glossary_present, top_score, top_chunk_id, glossary_forced, focus_fallback,
    filtered_anchor_terms)`` where ``reason`` is ``"low score"`` when matches
    exist but all fall below the threshold. ``fallback`` indicates that
    low-score chunks were returned. ``glossary_present`` is ``True`` if any
    candidate chunk contains glossary hints. ``top_score`` and ``top_chunk_id``
    reflect the best scoring chunk before filtering. ``glossary_forced`` is
    ``True`` when glossary chunks were injected due to an anchor match regardless
    of score. ``focus_fallback`` indicates that no focus anchors were found and
    all anchors were considered, while ``filtered_anchor_terms`` lists query terms
    filtered out due to focus restrictions.
    """
    if not query_text:
        return [], None, False, False, 0.0, None, False, False, []

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
        return [], None, False, False, 0.0, None, False, False, []

    try:
        query_vec = get_embedding_for_text(query_text)
    except Exception as exc:  # pragma: no cover - network
        logger.error("Embedding generation failed: %s", exc)
        return [], None, False, False, 0.0, None, False, False, []
    if not query_vec:
        return [], None, False, False, 0.0, None, False, False, []

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

    focus_qs = SymbolicMemoryAnchor.objects.filter(is_focus_term=True)
    focus_fallback = False
    if auto_expand or settings.DEBUG:
        anchor_qs = SymbolicMemoryAnchor.objects.all()
    elif focus_qs.exists():
        anchor_qs = focus_qs
    else:
        anchor_qs = SymbolicMemoryAnchor.objects.all()
        focus_fallback = True

    anchor_qs = anchor_qs.prefetch_related("tags")
    all_anchors = list(anchor_qs)
    anchor_matches = [
        a.slug for a in all_anchors if _anchor_in_query(a, query_text)
    ]
    if not (auto_expand or settings.DEBUG) and focus_qs.exists():
        all_slugs = list(SymbolicMemoryAnchor.objects.values_list("slug", flat=True))
        filtered_anchor_terms = [
            s
            for s in all_slugs
            if s.lower() in query_text.lower() and s not in [a.slug for a in all_anchors]
        ]
    else:
        filtered_anchor_terms = []
    for chunk in chunks:
        vec = chunk.embedding.vector if chunk.embedding else None
        if vec is None:
            logger.debug("Skipping chunk %s due to missing embedding", chunk.id)
            continue
        score = compute_similarity(query_vec, vec)
        if score < MIN_SCORE:
            logger.debug(
                "Skipping chunk %s due to low score %.3f", chunk.id, score
            )
            continue
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
            score += 0.2
            glossary_present = True
        if query_terms and (
            getattr(chunk, "is_glossary", False)
            or "glossary" in getattr(chunk, "tags", [])
        ):
            score += 0.15
        anchor_confidence = 0.0
        if chunk.anchor:
            if chunk.anchor.slug in anchor_matches:
                score += ANCHOR_BOOST
                anchor_confidence = 1.0
            else:
                anchor_confidence = 0.5
        logger.debug(
            "Retrieved chunk score: %.4f | contains_glossary=%s",
            score,
            contains_glossary,
        )
        scored.append((score, chunk, anchor_confidence))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0] if scored else 0.0
    top_chunk_id = str(scored[0][1].id) if scored else None
    # ``scored`` contains tuples of ``(score, chunk, anchor_confidence)`` so we
    # need to keep all three values when filtering. Previously this list
    # comprehension only unpacked ``score`` and ``chunk`` which caused a
    # ``ValueError`` when later code expected the anchor confidence value.
    filtered = [(s, c, conf) for s, c, conf in scored if s >= score_threshold]
    reason = None
    fallback = False

    strong_matches = filtered[:3]
    anchor_pairs = [
        p for p in scored if p[1].anchor and p[1].anchor.slug in anchor_matches
    ]
    glossary_anchor_pairs = []
    for p in scored:
        ch = p[1]
        if not getattr(ch, "is_glossary", False):
            continue
        match = False
        if ch.anchor and ch.anchor.slug in anchor_matches:
            match = True
        if any(t.lower() in query_text.lower() for t in query_terms.keys()):
            match = True
        if match and p[0] >= GLOSSARY_MIN_SCORE_OVERRIDE:
            glossary_anchor_pairs.append(p)
    if query_terms and anchor_matches and not glossary_anchor_pairs:
        reason = reason or "glossary missing"
    glossary_forced = False
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
        for i, (s, c, _conf) in enumerate(pairs, 1):
            logger.info("Fallback chunk %s score %.4f", i, s)
    else:
        return (
            [],
            None,
            False,
            glossary_present,
            top_score,
            top_chunk_id,
            False,
            focus_fallback,
            filtered_anchor_terms,
        )

    # Ensure anchor matched chunks are injected
    for pair in anchor_pairs:
        if pair not in pairs:
            pairs.append(pair)
            reason = reason or "forced anchor"
            fallback = True
    # Force glossary chunks for matched anchors
    for pair in glossary_anchor_pairs:
        if pair not in pairs:
            pairs.append(pair)
            glossary_forced = True
            reason = reason or "forced glossary"
            fallback = True

    pairs.sort(key=lambda x: x[0], reverse=True)

    result = []
    for score, chunk, anchor_conf in pairs:
        result.append(
            {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "score": round(score, 4),
                "text": chunk.text,
                "source_doc": chunk.document.title,
                "is_glossary": getattr(chunk, "is_glossary", False),
                "anchor_slug": getattr(getattr(chunk, "anchor", None), "slug", None),
                "anchor_confidence": anchor_conf,
                "fingerprint": getattr(chunk, "fingerprint", ""),
                "anchor_boost": ANCHOR_BOOST if (getattr(chunk, "anchor", None) and getattr(chunk.anchor, "slug", None) in anchor_matches) else 0,
            }
        )

    return (
        result,
        reason,
        fallback,
        glossary_present,
        top_score,
        top_chunk_id,
        glossary_forced,
        focus_fallback,
        filtered_anchor_terms,
    )


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
