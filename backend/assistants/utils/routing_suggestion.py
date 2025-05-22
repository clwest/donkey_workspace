from __future__ import annotations

from typing import List, Dict, Any

from assistants.models.assistant import Assistant, ChatSession
from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.vector_utils import compute_similarity


def suggest_assistant_for_context(
    context_summary: str,
    tags: List[str] | None = None,
    recent_messages: List[Dict[str, Any]] | None = None,
    top_n: int = 3,
) -> Dict[str, Any] | None:
    """Return the best matching assistants for a context summary."""
    tags = tags or []
    recent_messages = recent_messages or []

    text_parts = [context_summary or ""]
    for m in recent_messages[-5:]:
        content = m.get("content")
        if content:
            text_parts.append(content)
    text = " ".join(text_parts).strip()
    if not text:
        text = "context"

    try:
        embedding = get_embedding_for_text(text)
    except Exception:
        embedding = [0.0] * 1536

    results: List[Dict[str, Any]] = []
    for assistant in Assistant.objects.filter(is_active=True):
        score = 0.0
        reason = []

        if assistant.capability_embedding is not None:
            sim = compute_similarity(embedding, assistant.capability_embedding)
            score += sim
            if sim > 0.25:
                reason.append("capability match")

        skill_tags: List[str] = []
        for skill in assistant.skills.all():
            skill_tags.extend(skill.related_tags)
        overlap = len(set(t.lower() for t in tags) & set(t.lower() for t in skill_tags))
        if overlap:
            score += overlap * 0.1
            reason.append("tag overlap")

        active_sessions = ChatSession.objects.filter(
            assistant=assistant, ended_at__isnull=True
        ).count()
        if active_sessions:
            score -= min(active_sessions, 5) * 0.05
            if active_sessions > 0:
                reason.append("busy")

        results.append(
            {"assistant": assistant, "score": score, "reason": ", ".join(reason)}
        )

    if not results:
        return None

    results.sort(key=lambda r: r["score"], reverse=True)
    best = results[0]
    alternates = results[1:top_n]
    return {"best": best, "alternates": alternates}
