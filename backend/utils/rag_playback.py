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
) -> RAGPlaybackLog:
    """Persist chunk metadata for debugging playback."""
    meta = []
    anchor_terms = set()
    for info in chunks:
        anchors = info.get("matched_anchors", [])
        anchor_terms.update(anchors)
        meta.append(
            {
                "id": info.get("chunk_id"),
                "score": info.get("score_before_anchor_boost"),
                "boost": info.get("glossary_boost_applied", 0.0),
                "final_score": info.get("score"),
                "text": info.get("text", "")[:500],
                "matched_anchors": anchors,
                "fallback_used": info.get("final_score", 0.0)
                < info.get("fallback_threshold_used", 0.0),
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
    )


def log_rag_playback(*args, **kwargs) -> RAGPlaybackLog:
    """Backward compatible wrapper for ``record_rag_playback``."""
    return record_rag_playback(*args, **kwargs)

