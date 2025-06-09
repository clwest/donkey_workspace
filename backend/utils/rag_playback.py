from __future__ import annotations
from typing import List, Dict
from memory.models import RAGPlaybackLog


def record_rag_playback(
    query: str,
    assistant,
    memory_context,
    chunks: List[Dict],
    *,
    query_term: str = "",
    score_cutoff: float | None = None,
    fallback_reason: str | None = None,
    playback_type: str = RAGPlaybackLog.PlaybackType.MANUAL,
    demo_session_id: str | None = "",
) -> RAGPlaybackLog:
    """Persist chunk metadata for debugging playback."""
    meta = []
    anchor_terms = set()
    for info in chunks:
        anchors = info.get("matched_anchors", [])
        anchor_terms.update(anchors)
        is_fallback = info.get("final_score", 0.0) < info.get("fallback_threshold_used", 0.0)
        meta.append(
            {
                "id": info.get("chunk_id"),
                "score": info.get("score_before_anchor_boost"),
                "boost": info.get("glossary_boost_applied", 0.0),
                "final_score": info.get("score"),
                "text": info.get("text", "")[:500],
                "matched_anchors": anchors,
                "is_fallback": is_fallback,
                "anchor_match": info.get("was_anchor_match", False),
                "glossary_score": info.get("glossary_score", 0.0),
                "fallback_used": is_fallback,
            }
        )
    return RAGPlaybackLog.objects.create(
        assistant=assistant,
        query=query,
        query_term=query_term or query,
        score_cutoff=score_cutoff,
        fallback_reason=fallback_reason,
        playback_type=playback_type,
        memory_context=memory_context,
        chunks=meta,
        demo_session_id=demo_session_id or "",
    )


def log_rag_playback(*args, **kwargs) -> RAGPlaybackLog:
    """Backward compatible wrapper for ``record_rag_playback``."""
    return record_rag_playback(*args, **kwargs)

