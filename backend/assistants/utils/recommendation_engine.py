from __future__ import annotations

import logging
from typing import Optional, Dict, Any, Iterable

from assistants.models import Assistant, AssistantObjective
from memory.models import MemoryEntry
from assistants.utils.delegation_helpers import get_trust_score

logger = logging.getLogger(__name__)


def _candidate_assistants(current: Assistant) -> Iterable[Assistant]:
    """Return active assistants excluding the current one."""
    return Assistant.objects.filter(is_active=True).exclude(id=current.id)


def _score_from_trust(assistant: Assistant) -> float:
    trust = get_trust_score(assistant)
    avg = trust.get("average_score")
    return float(avg) if avg is not None else 0.0


def suggest_agent_for_task(current_assistant: Assistant, task_context: Any) -> Optional[Dict[str, Any]]:
    """Return the best assistant to delegate to for this context."""
    candidates = list(_candidate_assistants(current_assistant))
    if not candidates:
        return None

    keywords = []
    tag_names = []

    if isinstance(task_context, MemoryEntry):
        tag_names = list(task_context.tags.values_list("name", flat=True))
        if task_context.type:
            keywords.append(task_context.type)
    elif isinstance(task_context, AssistantObjective):
        keywords.extend(task_context.title.lower().split())
        if task_context.description:
            keywords.extend(task_context.description.lower().split())
    else:
        logger.warning("Unsupported context for recommendation: %s", type(task_context))
        return None

    best = None
    best_score = -1.0
    best_reason = ""

    for candidate in candidates:
        score = _score_from_trust(candidate)
        reason = None

        for tag in tag_names:
            if tag.lower() in candidate.specialty.lower():
                score += 0.6
                reason = f"Tag match '{tag}'"
                break

        if not reason:
            for kw in keywords:
                if kw.lower() in candidate.specialty.lower():
                    score += 0.5
                    reason = f"Specialty match '{kw}'"
                    break

        if score > best_score:
            best = candidate
            best_score = score
            best_reason = reason or "High trust score"

    if best is None:
        return None

    return {
        "assistant_id": str(best.id),
        "match_reason": best_reason,
        "score": round(best_score, 2),
    }

