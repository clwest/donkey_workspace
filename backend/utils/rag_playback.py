from __future__ import annotations
from typing import List, Dict
from memory.models import RAGPlaybackLog


def log_rag_playback(query: str, assistant, memory_context, chunks: List[Dict]) -> RAGPlaybackLog:
    """Persist chunk metadata for debugging playback."""
    meta = []
    for info in chunks:
        meta.append(
            {
                "id": info.get("chunk_id"),
                "score": info.get("score_before_anchor_boost"),
                "boost": info.get("glossary_boost_applied", 0.0),
                "final_score": info.get("score"),
                "text": info.get("text", "")[:500],
                "matched_anchors": info.get("matched_anchors", []),
                "fallback_used": info.get("final_score", 0.0) < info.get("fallback_threshold_used", 0.0),
            }
        )
    return RAGPlaybackLog.objects.create(
        assistant=assistant,
        query=query,
        memory_context=memory_context,
        chunks=meta,
    )

