from __future__ import annotations

import logging
from typing import Optional, Dict, Any, Iterable

from django.utils import timezone
from assistants.models import (
    Assistant,
    AssistantObjective,
    DelegationEvent,
    DelegationStrategy,
)
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

    strategy = getattr(current_assistant, "delegation_strategy", None)
    prefer_specialists = strategy.prefer_specialists if strategy else True
    trust_threshold = strategy.trust_threshold if strategy else 0.75
    avoid_failures = strategy.avoid_recent_failures if strategy else True
    max_active = strategy.max_active_delegations if strategy else 5

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
    best_adjusted = False
    best_failures = 0

    now = timezone.now()
    week_ago = now - timezone.timedelta(days=7)

    for candidate in candidates:
        trust_score = _score_from_trust(candidate)
        if trust_score < trust_threshold * 5:
            continue

        recent_failures = DelegationEvent.objects.filter(
            child_assistant=candidate, score__lte=2, created_at__gte=week_ago
        ).count()
        if avoid_failures and recent_failures >= 3:
            continue

        active_count = DelegationEvent.objects.filter(
            child_assistant=candidate, completed=False
        ).count()
        if active_count >= max_active:
            continue

        score = trust_score
        reason = None
        adjusted = False

        for tag in tag_names:
            if tag.lower() in candidate.specialty.lower():
                score += 2
                reason = f"Tag match '{tag}'"
                break

        if prefer_specialists and not reason:
            for kw in keywords:
                if kw.lower() in candidate.specialty.lower():
                    score += 1.5
                    reason = f"Specialty match '{kw}'"
                    break

        if trust_score >= 4:
            score += 1
            adjusted = True

        if score > best_score:
            best = candidate
            best_score = score
            best_reason = reason or "High trust"
            best_adjusted = adjusted
            best_failures = recent_failures

    if best is None:
        return None

    return {
        "assistant_id": str(best.id),
        "match_reason": best_reason,
        "score": round(best_score, 2),
        "adjusted_for_trust": best_adjusted,
        "recent_failures": best_failures,
    }

