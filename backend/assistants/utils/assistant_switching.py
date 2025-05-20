from __future__ import annotations

from typing import Dict, Any, Optional

from assistants.models import ChatSession, Assistant
from assistants.utils.routing_suggestion import suggest_assistant_for_context


def suggest_assistant_switch(session: ChatSession) -> Optional[Dict[str, Any]]:
    """Return a better suited assistant for this session if one exists."""
    recent = list(
        session.messages.order_by("-created_at").values("role", "content", "feedback")[
            :5
        ]
    )
    context = " ".join(m["content"] for m in reversed(recent))
    tags = [m["feedback"] for m in recent if m.get("feedback")]

    result = suggest_assistant_for_context(
        context_summary=context, tags=tags, recent_messages=recent
    )
    if not result:
        return None

    current = session.assistant
    candidates = [result["best"]] + result.get("alternates", [])
    current_score = None
    best = None
    for item in candidates:
        if item["assistant"] == current:
            current_score = item["score"]
        elif best is None:
            best = item
    if best is None:
        return None
    if current_score is None:
        current_score = 0.0
    confidence = round(best["score"] - current_score, 2)
    return {
        "assistant": best["assistant"],
        "score": best["score"],
        "reason": best.get("reason", ""),
        "confidence": confidence,
    }
