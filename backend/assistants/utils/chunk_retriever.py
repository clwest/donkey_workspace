from __future__ import annotations
import logging
import uuid
from typing import List, Dict, Tuple, Optional
from django.shortcuts import get_object_or_404
from assistants.models.assistant import Assistant
from assistants.models.project import AssistantProject

# Boost acronym chunks
from intel_core.services import AcronymGlossaryService
from memory.models import SymbolicMemoryAnchor
from intel_core.utils.glossary_tagging import _match_anchor

# Import directly from helpers_io to avoid __init__ fallbacks
from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.vector_utils import compute_similarity
from embeddings.models import EMBEDDING_LENGTH
import math
from django.conf import settings

# Minimum score required to bypass normal filtering when forcing
# glossary chunks for an anchor match
GLOSSARY_MIN_SCORE_OVERRIDE = 0.15
# Minimum similarity score for a chunk to be considered at all.
MIN_SCORE = 0.05
ANCHOR_FORCE_MIN_SCORE = 0.1

# Score boost applied when a chunk's anchor matches the query.
ANCHOR_BOOST = getattr(settings, "RAG_ANCHOR_BOOST", 0.1)
# Boost factor applied when a chunk contains glossary matches
GLOSSARY_BOOST_FACTOR = getattr(settings, "RAG_GLOSSARY_BOOST_FACTOR", 0.2)
# Threshold below which glossary chunks are considered weak
GLOSSARY_WEAK_THRESHOLD = getattr(settings, "GLOSSARY_WEAK_THRESHOLD", 0.2)
# Boost when a term is pulled from recent reflections
REFLECTION_BOOST = getattr(settings, "RAG_REFLECTION_BOOST", 0.15)

logger = logging.getLogger(__name__)


def is_valid_uuid(value: str) -> bool:
    """Return True if the given value is a valid UUID string."""
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, TypeError):
        return False


def _anchor_in_query(anchor: SymbolicMemoryAnchor, text: str) -> bool:
    """Return True if ``text`` mentions ``anchor`` via slug, label or tags."""
    q = text.lower()
    if anchor.slug.lower() in q or anchor.label.lower() in q:
        return True
    if (
        anchor.tags.filter(slug__in=q.split()).exists()
        or anchor.tags.filter(name__in=q.split()).exists()
    ):
        return True
    matched, _ = _match_anchor(anchor, text)
    return matched


def _search_summary_hits(
    query_vec: list, doc_ids: List[str], limit: int = 3
) -> List[dict]:
    """Return summary-level fallback results for the given documents."""
    from intel_core.models import Document

    docs = Document.objects.filter(id__in=doc_ids).exclude(summary__isnull=True)
    scored: List[tuple[float, Document]] = []
    for doc in docs:
        if not doc.summary:
            continue
        try:
            vec = get_embedding_for_text(doc.summary)
        except Exception:  # pragma: no cover - network
            continue
        if not vec:
            continue
        score = compute_similarity(query_vec, vec)
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, doc in scored[:limit]:
        results.append(
            {
                "doc_id": str(doc.id),
                "score": round(score, 4),
                "summary_excerpt": (doc.summary or "")[:120],
            }
        )
    return results


def get_glossary_terms_from_reflections(memory_context_id: Optional[str]) -> List[str]:
    """Return list of glossary terms mentioned in recent reflections."""
    from memory.models import MemoryEntry, SymbolicMemoryAnchor

    reflections = MemoryEntry.objects.filter(type="reflection").order_by("-created_at")
    if memory_context_id:
        reflections = reflections.filter(context_id=memory_context_id)
    reflections = reflections[:25]
    anchors = list(SymbolicMemoryAnchor.objects.all())
    terms: set[str] = set()
    for mem in reflections:
        text = (mem.summary or mem.event or "").lower()
        for anc in anchors:
            if anc.slug.lower() in text or anc.label.lower() in text:
                terms.add(anc.slug)
        terms.update(mem.tags.values_list("slug", flat=True))
    return list(terms)


def get_relevant_chunks(
    assistant_id: Optional[str],
    query_text: str,
    *,
    memory_context_id: Optional[str] = None,
    project_id: Optional[str] = None,
    document_id: Optional[str] = None,
    score_threshold: float = 0.65,
    keywords: Optional[List[str]] = None,
    fallback_min: float = 0.5,
    fallback_limit: int = 2,
    auto_expand: bool = False,
    force_chunks: bool = False,
    force_fallback: bool = False,
    min_rag_score: float = 0.3,
    min_score: float = 0.6,
    debug: bool = False,
    log_diagnostic: bool = False,
) -> Tuple[
    List[Dict[str, object]],
    Optional[str],
    bool,
    bool,
    float,
    Optional[str],
    bool,
    bool,
    List[str],
    Dict[str, object],
]:
    """Return top matching chunks and an optional ignore reason.

    Results are filtered by ``score_threshold`` and optionally reranked if
    ``keywords`` are provided.  The return value is ``(chunks, reason, fallback,
    glossary_present, top_score, top_chunk_id, glossary_forced, focus_fallback,
    filtered_anchor_terms, debug_info)`` where ``reason`` is ``"low score"`` when matches
    exist but all fall below the threshold. ``fallback`` indicates that
    low-score chunks were returned. ``glossary_present`` is ``True`` if any
    candidate chunk contains glossary hints. ``top_score`` and ``top_chunk_id``
    reflect the best scoring chunk before filtering. ``glossary_forced`` is
    ``True`` when glossary chunks were injected due to an anchor match regardless
    of score. ``focus_fallback`` indicates that no focus anchors were found and
    all anchors were considered, while ``filtered_anchor_terms`` lists query terms
    filtered out due to focus restrictions. ``debug_info`` now also includes
    ``override_map`` and per-chunk candidate details. ``force_chunks`` bypasses
    score filtering and always returns the top 3 chunks. ``force_fallback``
    allows zero-score or weak chunks to be returned when no valid options remain.
    ``min_rag_score`` triggers summary-level fallback when the best score is
    below the threshold. ``min_score`` controls the minimum score allowed when
    glossary boosting is applied.
    """
    if not query_text:
        return (
            [],
            None,
            False,
            False,
            0.0,
            None,
            False,
            False,
            [],
            {},
        )

    logger.info("🔍 Searching document embeddings for query: %s", query_text[:80])

    assistant = None
    if assistant_id:
        if is_valid_uuid(assistant_id):
            assistant = Assistant.objects.filter(id=assistant_id).first()
            if not assistant:
                assistant = Assistant.objects.filter(slug=assistant_id).first()
        else:
            assistant = Assistant.objects.filter(slug=assistant_id).first()
        if not assistant:
            logger.warning("Assistant %s not found", assistant_id)

    if memory_context_id is None and assistant and assistant.memory_context_id:
        memory_context_id = str(assistant.memory_context_id)
    elif memory_context_id is None and assistant and not assistant.memory_context_id:
        logger.warning(
            "[RAG] Assistant %s missing memory_context_id; using global scope",
            assistant.slug,
        )
    chunk_ids: List[str] = []
    doc_ids: List[str] = []

    if memory_context_id:
        from django.contrib.contenttypes.models import ContentType
        from memory.models import MemoryEntry
        from intel_core.models import DocumentChunk

        ct = ContentType.objects.get_for_model(DocumentChunk)
        chunk_ids = list(
            MemoryEntry.objects.filter(
                context_id=memory_context_id, linked_content_type=ct
            ).values_list("linked_object_id", flat=True)
        )
        logger.info(
            "[RAG] Scope enforced: memory_context_id=%s | chunks searched=%d",
            memory_context_id,
            len(chunk_ids),
        )
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

    if not chunk_ids and not doc_ids:
        return (
            [],
            None,
            False,
            False,
            0.0,
            None,
            False,
            False,
            [],
            {},
        )

    try:
        query_vec = get_embedding_for_text(query_text)
    except Exception as exc:  # pragma: no cover - network
        logger.error("Embedding generation failed: %s", exc)
        return (
            [],
            None,
            False,
            False,
            0.0,
            None,
            False,
            False,
            [],
            {},
        )
    if not query_vec:
        return (
            [],
            None,
            False,
            False,
            0.0,
            None,
            False,
            False,
            [],
            {},
        )

    from intel_core.utils.chunk_retriever import fetch_chunks

    chunks = fetch_chunks(
        doc_ids if chunk_ids == [] else None,
        chunk_ids=chunk_ids if chunk_ids else None,
        repair=debug or settings.DEBUG,
    )

    logger.debug(
        "[RAG Search] Docs=%s Chunks=%s -> %d chunks",
        doc_ids,
        chunk_ids[:10] if chunk_ids else None,
        len(chunks),
    )
    if chunks:
        logger.debug("Chunk IDs returned: %s", [str(c.id) for c in chunks[:20]])
    force_keywords = [
        "opening line",
        "first sentence",
        "beginning of the video",
        "speaker said",
        "quote",
    ]
    force_inject = any(k in query_text.lower() for k in force_keywords)

    scored = []
    debug_candidates: list[dict[str, object]] = []
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
    anchor_matches = [a.slug for a in all_anchors if _anchor_in_query(a, query_text)]
    logger.debug("[Glossary Tracker] query anchors=%s", anchor_matches)
    reflection_terms = set(get_glossary_terms_from_reflections(memory_context_id))
    if not (auto_expand or settings.DEBUG) and focus_qs.exists():
        all_slugs = list(SymbolicMemoryAnchor.objects.values_list("slug", flat=True))
        filtered_anchor_terms = [
            s
            for s in all_slugs
            if s.lower() in query_text.lower()
            and s not in [a.slug for a in all_anchors]
        ]
    else:
        filtered_anchor_terms = []
    for chunk in chunks:
        if chunk.embedding and chunk.embedding_status != "embedded":
            logger.warning(
                "Chunk %s has embedding_id %s but status %s; fixing",
                chunk.id,
                getattr(chunk.embedding, "id", None),
                chunk.embedding_status,
            )
            chunk.embedding_status = "embedded"
            chunk.save(update_fields=["embedding_status"])
        if getattr(chunk, "embedding_status", "embedded") != "embedded":
            logger.warning(
                "\u26a0\ufe0f RAG selected chunk %s with embedding_status=%s",
                chunk.id,
                getattr(chunk, "embedding_status", "unknown"),
            )
            continue
        vec = chunk.embedding.vector if chunk.embedding else None
        if vec is None:
            logger.debug("Skipping chunk %s due to missing embedding", chunk.id)
            continue
        if not isinstance(vec, list) or len(vec) != EMBEDDING_LENGTH:
            logger.warning(
                "Chunk %s has malformed embedding length=%s",
                chunk.id,
                len(vec) if isinstance(vec, list) else "N/A",
            )
            continue
        if any(math.isnan(v) for v in vec):
            logger.warning("NaN values detected in embedding for chunk %s", chunk.id)
            continue
        score = compute_similarity(query_vec, vec)
        raw_score = score
        if assistant and assistant.preferred_rag_vector is not None:
            try:
                pref_score = compute_similarity(assistant.preferred_rag_vector, vec)
                score += pref_score * 0.1
            except Exception as exc:  # pragma: no cover - log mismatch
                logger.warning("Preference similarity failed: %s", exc)
        anchor_weight = 0.0
        if assistant and assistant.anchor_weight_profile and chunk.anchor:
            weight = assistant.anchor_weight_profile.get(chunk.anchor.slug)
            if weight:
                anchor_weight = float(weight)
                score *= 1 + anchor_weight
        if chunk.anchor and chunk.anchor.slug in query_text.lower():
            score += 0.05
        length_norm = min(len(chunk.text) / 500, 1.0)
        score *= 0.6 + 0.4 * length_norm
        if score <= 0.0 and not force_fallback:
            logger.debug("Skipping chunk %s due to zero score", chunk.id)
            continue
        if score < MIN_SCORE and not (
            chunk.anchor and chunk.anchor.slug in anchor_matches
        ):
            logger.debug("Skipping chunk %s due to low score %.3f", chunk.id, score)
            if score < 0.2:
                logger.info(
                    "[RAG Filter] %s dropped due to score %.3f < 0.2",
                    chunk.id,
                    score,
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
        # Boost using precomputed glossary_score but keep track of glossary hit
        score += getattr(chunk, "glossary_score", 0.0) * GLOSSARY_BOOST_FACTOR
        glossary_hit = (
            contains_glossary
            or getattr(chunk, "is_glossary", False)
            or (
                query_terms
                and (
                    getattr(chunk, "is_glossary", False)
                    or "glossary" in getattr(chunk, "tags", [])
                )
            )
        )
        glossary_boost = getattr(chunk, "glossary_boost", 0.0)
        if glossary_hit:
            score += glossary_boost
        reflection_boost = 0.0
        reflection_hit = False
        if reflection_terms:
            if chunk.anchor and chunk.anchor.slug in reflection_terms:
                reflection_hit = True
            elif any(t in chunk.text.lower() for t in reflection_terms):
                reflection_hit = True
        if reflection_hit:
            reflection_boost = REFLECTION_BOOST
            score += reflection_boost
        if not getattr(chunk, "fingerprint", ""):
            score -= 0.05
        weak_glossary = (
            getattr(chunk, "is_glossary", False)
            and getattr(chunk, "glossary_score", 0.0) < GLOSSARY_WEAK_THRESHOLD
        ) or getattr(chunk, "weak", False)
        if weak_glossary and not force_fallback:
            logger.debug("Skipping weak glossary chunk %s", chunk.id)
            continue
        if (
            getattr(chunk, "is_glossary", False)
            and score < GLOSSARY_MIN_SCORE_OVERRIDE
            and (not chunk.anchor or chunk.anchor.slug not in anchor_matches)
            and not force_chunks
        ):
            logger.debug("Skipping low-score glossary chunk %s", chunk.id)
            continue
        anchor_confidence = 0.0
        if chunk.anchor:
            if chunk.anchor.slug in anchor_matches:
                score += ANCHOR_BOOST
                anchor_confidence = 1.0
            else:
                anchor_confidence = 0.5
        logger.info(
            "[RAG] Chunk %s | Raw Score: %.4f | Glossary Boost: %.4f | Final Score: %.4f",
            chunk.id,
            raw_score,
            glossary_boost if glossary_hit else 0.0,
            score,
        )
        scored.append(
            (
                score,
                chunk,
                anchor_confidence,
                raw_score,
                glossary_boost if glossary_hit else 0.0,
                glossary_hit,
                reflection_boost,
            )
        )
        debug_candidates.append(
            {
                "id": str(chunk.id),
                "was_anchor_match": bool(
                    chunk.anchor and chunk.anchor.slug in anchor_matches
                ),
                "raw_score": round(raw_score, 4),
                "final_score": round(score, 4),
                "glossary_boost": round(glossary_boost if glossary_hit else 0.0, 4),
                "glossary_hit": glossary_hit,
                "reflection_boost": round(reflection_boost, 4),
                "reflection_hit": reflection_hit,
            }
        )

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0] if scored else 0.0
    top_chunk_id = str(scored[0][1].id) if scored else None
    top_raw_score = scored[0][3] if scored else 0.0
    top_boost = scored[0][4] if scored else 0.0

    summary_hits: List[dict] = []
    fallback_type = None
    if top_score < min_rag_score and query_vec:
        summary_hits = _search_summary_hits(query_vec, doc_ids)
        if summary_hits:
            fallback_type = "summary"
    # ``scored`` contains tuples of ``(score, chunk, anchor_confidence, raw_score, glossary_boost, glossary_hit, reflection_boost)``
    # so we keep all fields intact when filtering.
    filtered = (
        [
            (s, c, conf, raw, boost, ghit, rboost)
            for s, c, conf, raw, boost, ghit, rboost in scored
            if s >= score_threshold or (ghit and s >= min_score)
        ]
        if not force_chunks
        else scored
    )
    warnings: List[str] = []
    score_list = [s for s, _c, _conf, _raw, _b, _g, _r in scored]
    max_score = max(score_list) if score_list else 0.0
    if not filtered and score_list and max_score < 0.15:
        warnings.append(
            f"\u26a0\ufe0f All chunk scores below threshold ({max_score:.3f}) \u2014 RAG fallback in effect."
        )
    reason = None
    fallback = False

    strong_matches = filtered[:3]
    anchor_pairs = [
        p
        for p in scored
        if p[1].anchor
        and p[1].anchor.slug in anchor_matches
        and p[0] >= ANCHOR_FORCE_MIN_SCORE
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
    glossary_chunk_ids = [str(p[1].id) for p in glossary_anchor_pairs]
    logger.debug("[Glossary Tracker] glossary_chunk_ids=%s", glossary_chunk_ids)
    if query_terms and anchor_matches and not glossary_anchor_pairs:
        reason = reason or "glossary missing"
    glossary_forced = False
    if force_chunks and scored:
        reason = reason or "forced override"
        fallback = True
        fallback_type = fallback_type or "chunk"
        pairs = scored[: max(1, fallback_limit)]
    elif force_inject and scored:
        reason = reason or "forced"
        fallback = True
        fallback_type = fallback_type or "chunk"
        pairs = scored[: max(1, fallback_limit)]
    elif strong_matches:
        pairs = strong_matches
    elif scored:
        fallback = True
        reason = "low score"
        logger.info("RAG fallback: using low-score chunks")
        # take top ``fallback_limit`` above ``fallback_min`` if any
        candidates = [
            p for p in scored if p[0] >= fallback_min and (force_fallback or p[0] > 0.0)
        ]
        if not candidates:
            logger.info("All candidate chunks rejected; forcing fallback")
            candidates = scored
        pairs = candidates[: max(1, fallback_limit)]
        for i, (s, c, _conf, _rs, _boost, _ghit, _rboost) in enumerate(pairs, 1):
            logger.info(
                "[Fallback] Using Chunk ID %s | Score: %.4f | Reason: %s",
                c.id,
                s,
                reason or "unknown",
            )
        fallback_type = fallback_type or "chunk"
    else:
        logger.info(
            '[RAG] Fallback for assistant=%s, context=%s, query="%s" - reason: no matches',
            getattr(assistant, "slug", assistant_id),
            memory_context_id,
            query_text,
        )
        debug_info = {
            "retrieved_chunk_count": len(debug_candidates),
            "anchor_matched_chunks": [
                d["id"] for d in debug_candidates if d.get("was_anchor_match")
            ],
            "filtered_out_chunks": [d["id"] for d in debug_candidates],
            "reason_not_included": {d["id"]: "no_candidate" for d in debug_candidates},
            "override_map": {},
            "candidates": debug_candidates,
        }
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
            debug_info,
        )

    override_map: dict[str, str] = {}
    # Ensure anchor matched chunks are injected
    for pair in anchor_pairs:
        if pair not in pairs:
            pairs.append(pair)
            reason = reason or "forced anchor"
            fallback = True
            override_map[str(pair[1].id)] = "anchor-match"
    # Force glossary chunks for matched anchors
    for pair in glossary_anchor_pairs:
        if pair not in pairs:
            pairs.append(pair)
            glossary_forced = True
            reason = reason or "forced glossary"
            fallback = True
            override_map[str(pair[1].id)] = "anchor-match"

    # Guarantee at least one anchor override
    if anchor_pairs and not any(
        p[1].id in [c[1].id for c in pairs] for p in anchor_pairs
    ):
        best = max(anchor_pairs, key=lambda x: x[0])
        if best not in pairs:
            pairs.append(best)
        reason = reason or "anchor override"
        fallback = True
        override_map[str(best[1].id)] = "anchor-match"

    pairs.sort(key=lambda x: x[0], reverse=True)

    included_ids = [str(p[1].id) for p in pairs]
    for info in debug_candidates:
        cid = info["id"]
        info["was_filtered_out"] = cid not in included_ids
        info["forced_included"] = cid in override_map
        info["override_reason"] = override_map.get(cid)
        if info["was_filtered_out"]:
            info["excluded_reason"] = (
                "score < threshold"
                if info["final_score"] < score_threshold
                else "top-k drop"
            )
        else:
            info["excluded_reason"] = None
        logger.debug(
            "[RAG Result] Chunk %s | Score: %.4f | Forced: %s | Reason: %s",
            cid,
            info["final_score"],
            info["forced_included"],
            info.get("override_reason"),
        )
        if info["was_anchor_match"] and info["was_filtered_out"]:
            logger.warning(
                "[RAG ERROR] Anchor-linked chunk %s missing from results — expected forced inclusion.",
                cid,
            )

    result = []
    fallback_ids: List[str] = []
    fallback_scores: List[float] = []
    for score, chunk, anchor_conf, raw_score, g_boost, g_hit, r_boost in pairs:
        if chunk.embedding_status != "embedded":
            logger.warning(
                "\u26a0\ufe0f Chunk %s selected but not embedded (status=%s)",
                chunk.id,
                chunk.embedding_status,
            )
        if fallback and score < score_threshold:
            fallback_ids.append(str(chunk.id))
            fallback_scores.append(round(score, 4))
        info = {
            "chunk_id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "score": round(score, 4),
            "score_before_anchor_boost": round(raw_score, 4),
            "score_after_anchor_boost": round(score, 4),
            "glossary_boost_applied": round(g_boost, 4),
            "reflection_boost_applied": round(r_boost, 4),
            "fallback_threshold_used": (
                score_threshold if score >= score_threshold else min_score
            ),
            "text": chunk.text,
            "source_doc": chunk.document.title,
            "is_glossary": getattr(chunk, "is_glossary", False),
            "anchor_slug": getattr(getattr(chunk, "anchor", None), "slug", None),
            "anchor_confidence": anchor_conf,
            "fingerprint": getattr(chunk, "fingerprint", ""),
            "tokens": getattr(chunk, "tokens", 0),
            "glossary_score": getattr(chunk, "glossary_score", 0.0),
            "matched_anchors": getattr(chunk, "matched_anchors", []),
            "embedding_status": getattr(chunk, "embedding_status", "embedded"),
            "anchor_boost": (
                ANCHOR_BOOST
                if (
                    getattr(chunk, "anchor", None)
                    and getattr(chunk.anchor, "slug", None) in anchor_matches
                )
                else 0
            ),
            "override_reason": override_map.get(str(chunk.id)),
            "forced_included": str(chunk.id) in override_map,
            "was_anchor_match": bool(
                chunk.anchor and chunk.anchor.slug in anchor_matches
            ),
            "was_filtered_out": False,
            "final_score": round(score, 4),
            "forced_inclusion_reason": override_map.get(str(chunk.id)),
        }
        if reason:
            info["debug_log"] = reason
        result.append(info)

    debug_info = {
        "retrieved_chunk_count": len(debug_candidates),
        "anchor_matched_chunks": [
            d["id"] for d in debug_candidates if d.get("was_anchor_match")
        ],
        "filtered_out_chunks": [
            d["id"] for d in debug_candidates if d.get("was_filtered_out")
        ],
        "reason_not_included": {
            d["id"]: d.get("excluded_reason")
            for d in debug_candidates
            if d.get("was_filtered_out")
        },
        "override_map": override_map,
        "candidates": debug_candidates,
        "fallback_summaries": summary_hits,
        "fallback_type": fallback_type or ("chunk" if fallback else None),
        "weak_chunks_used": fallback,
        "fallback_chunk_ids": fallback_ids,
        "fallback_chunk_scores": fallback_scores,
        "top_raw_score": top_raw_score,
        "top_glossary_boost": top_boost,
        "top_reflection_boost": max((p[6] for p in scored), default=0.0),
        "reflection_hits": [
            d["id"] for d in debug_candidates if d.get("reflection_hit")
        ],
        "warnings": warnings,
    }
    logger.debug("[Glossary Tracker] fallback_scores=%s", fallback_scores)

    used_chunk_ids = [str(p[1].id) for p in pairs]
    if memory_context_id and used_chunk_ids:
        from django.contrib.contenttypes.models import ContentType
        from memory.models import MemoryEntry
        from intel_core.models import DocumentChunk

        ct = ContentType.objects.get_for_model(DocumentChunk)
        MemoryEntry.objects.filter(
            context_id=memory_context_id,
            linked_content_type=ct,
            linked_object_id__in=used_chunk_ids,
        ).update(was_used_in_chat=True)

    if fallback or fallback_type == "summary":
        reason_text = reason or (
            f"score < {top_score:.2f}"
            if fallback_type != "summary"
            else f"score < {min_rag_score}"
        )
        logger.info(
            '[RAG] Fallback for assistant=%s, context=%s, query="%s" - reason: %s',
            getattr(assistant, "slug", assistant_id),
            memory_context_id,
            query_text,
            reason_text,
        )
        try:
            from assistants.models import AssistantTimelineLog

            anchor_missed = ""
            if anchor_matches:
                for slug in anchor_matches:
                    if not any(c.get("anchor_slug") == slug for c in result):
                        anchor_missed = slug
                        break

            AssistantTimelineLog.objects.create(
                assistant=assistant,
                log_type="rag_fallback",
                anchor=anchor_missed,
                fallback_reason=reason or "",
                query_text=query_text,
                chunks_retrieved=len(result),
                fallback_triggered=True,
            )
        except Exception:
            pass

    logger.debug("[RAG Final] Returning chunks: %s", [r["chunk_id"] for r in result])

    if log_diagnostic and assistant_id:
        try:
            from utils.rag_diagnostic import log_rag_diagnostic

            assistant = (
                Assistant.objects.filter(id=assistant_id).first()
                or Assistant.objects.filter(slug=assistant_id).first()
            )
            if assistant:
                rag_meta = {
                    "used_chunks": result,
                    "rag_fallback": fallback,
                    "anchor_hits": [
                        c.get("anchor_slug") for c in result if c.get("anchor_slug")
                    ],
                    "retrieval_score": top_score,
                    "fallback_reason": reason,
                    **debug_info,
                }
                log_rag_diagnostic(
                    assistant,
                    query_text,
                    rag_meta,
                    memory_context_id=memory_context_id,
                )
        except Exception:
            pass

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
        debug_info,
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


def get_rag_chunk_debug(
    assistant_id: str, query_text: str, *, disable_scope: bool = False
) -> dict:
    """Return chunk matches split into normal and fallback sets."""
    assistant = None
    if not disable_scope:
        assistant = Assistant.objects.filter(id=assistant_id).first()

    memory_context = None
    if assistant and assistant.memory_context_id is not None:
        memory_context = str(assistant.memory_context_id)

    (
        chunks,
        reason,
        fallback,
        glossary_present,
        top_score,
        _,
        glossary_forced,
        _,
        _,
        debug_info,
    ) = get_relevant_chunks(
        assistant_id,
        query_text,
        memory_context_id=memory_context,
        debug=True,
    )

    fallback_ids = set(debug_info.get("fallback_chunk_ids", []))
    matched = [c for c in chunks if c.get("chunk_id") not in fallback_ids]
    fallback_chunks = [c for c in chunks if c.get("chunk_id") in fallback_ids]
    return {
        "matched_chunks": matched,
        "fallback_chunks": fallback_chunks,
        "scores": {c["chunk_id"]: c["score"] for c in chunks},
        "glossary_scores": {
            c["chunk_id"]: c.get("glossary_score", 0.0) for c in chunks
        },
        "fallback_triggered": fallback,
        "glossary_present": glossary_present,
        "glossary_misses": debug_info.get("anchor_misses", []),
        "retrieval_score": top_score,
        "reason": reason,
        "glossary_forced": glossary_forced,
    }
