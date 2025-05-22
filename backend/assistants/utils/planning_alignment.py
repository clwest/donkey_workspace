from __future__ import annotations

from collections import Counter
from typing import Iterable, Optional, Dict, Any

from assistants.models.thoughts import AssistantThoughtLog
from mcp_core.models import NarrativeThread


def _mood_stats(thoughts: Iterable[AssistantThoughtLog]) -> tuple[Dict[str, int], str]:
    moods = [t.mood for t in thoughts if getattr(t, "mood", None)]
    counts = Counter(moods)
    volatility = "stable"
    if len(moods) > 1:
        changes = sum(1 for a, b in zip(moods, moods[1:]) if a != b)
        if changes / (len(moods) - 1) > 0.5:
            volatility = "volatile"
    return dict(counts), volatility


def suggest_planning_realignment(
    thread: NarrativeThread,
    thought_logs: Iterable[AssistantThoughtLog],
    objective_title: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a simple planning realignment suggestion."""
    dist, volatility = _mood_stats(thought_logs)
    continuity = thread.continuity_score or 0.0

    actions = []
    if continuity < 0.5:
        actions.append("reduce scope or reconnect recent events")
    if volatility == "volatile":
        actions.append("establish consistent tone")
    if not actions:
        actions.append("no major changes required")

    proposed_objective = objective_title or thread.long_term_objective
    if continuity < 0.4 and proposed_objective:
        proposed_objective = f"Focus: {proposed_objective}"

    summary = "; ".join(actions)
    return {
        "summary": summary,
        "proposed_objective": proposed_objective,
        "mood_distribution": dist,
        "mood_volatility": volatility,
        "suggested_action": summary,
        "add_milestones": [],
        "remove_milestones": [],
    }

