from typing import Iterable, Dict
from django.db import models
from django.utils import timezone
from assistants.models import Assistant
from assistants.models.badge import Badge
from memory.models import SymbolicMemoryAnchor
from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog
from assistants.models.command_log import AssistantCommandLog


def _collect_stats(assistant: Assistant) -> Dict[str, int]:
    """Gather badge-related statistics for an assistant."""
    acquired = SymbolicMemoryAnchor.objects.filter(assistant=assistant).count()
    reinforced = SymbolicMemoryAnchor.objects.filter(reinforced_by=assistant).count()
    reflections = AssistantReflectionLog.objects.filter(assistant=assistant).count()
    improved_replays = ReflectionReplayLog.objects.filter(
        assistant=assistant, new_score__gt=models.F("old_score")
    ).count()
    cli_runs = AssistantCommandLog.objects.filter(assistant=assistant).count()
    cli_repairs = AssistantCommandLog.objects.filter(
        assistant=assistant, command__icontains="repair"
    ).count()
    return {
        "acquired": acquired,
        "reinforced": reinforced,
        "reflections": reflections,
        "improved_replays": improved_replays,
        "glossary_score": assistant.glossary_score,
        "badge_count": len(assistant.skill_badges or []),
        "cli_runs": cli_runs,
        "cli_repairs": cli_repairs,
    }


def _evaluate(criteria: str, context: Dict[str, int | float | Assistant | set]) -> bool:
    try:
        return bool(eval(criteria, {}, context))
    except Exception:
        return False


def update_assistant_badges(
    assistant: Assistant,
    manual: Dict[str, bool] | None = None,
    override: bool | None = False,
) -> None:
    """Update skill_badges on the given assistant.

    Parameters
    ----------
    assistant: Assistant
        Assistant to update.
    manual: Dict[str, bool] | None
        Mapping of badge slugs to True/False to force add/remove.
    override: bool
        If True, manual assignments override automatic criteria evaluation.
    """

    badges = set(assistant.skill_badges or [])
    stats = _collect_stats(assistant)
    context = {**stats, "assistant": assistant, "badges": badges}

    for badge in Badge.objects.all():
        auto_assign = False
        if badge.criteria:
            auto_assign = _evaluate(badge.criteria, context)

        if auto_assign:
            badges.add(badge.slug)
        else:
            badges.discard(badge.slug)

    if manual:
        for slug, state in manual.items():
            if state:
                badges.add(slug)
            elif override:
                badges.discard(slug)

    old_badges = set(assistant.skill_badges or [])
    assistant.skill_badges = sorted(badges)
    if old_badges != badges:
        history = assistant.badge_history or []
        history.append(
            {
                "badges": sorted(badges),
                "timestamp": timezone.now().isoformat(),
            }
        )
        assistant.badge_history = history[-20:]
        assistant.save(update_fields=["skill_badges", "badge_history"])


def filter_assistants_by_badge(badges: Iterable[str]):
    """Return queryset of assistants having all given badges."""
    qs = Assistant.objects.all()
    for badge in badges:
        qs = qs.filter(skill_badges__contains=[badge])
    return qs
