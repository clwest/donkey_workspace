from typing import Iterable
from django.db import models
from assistants.models import Assistant
from assistants.models.badge import Badge
from memory.models import SymbolicMemoryAnchor
from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog


def update_assistant_badges(assistant: Assistant) -> None:
    """Update skill_badges on the given assistant."""
    badges = set(assistant.skill_badges or [])

    acquired = SymbolicMemoryAnchor.objects.filter(assistant=assistant).count()
    reinforced = SymbolicMemoryAnchor.objects.filter(reinforced_by=assistant).count()
    reflections = AssistantReflectionLog.objects.filter(assistant=assistant).count()
    improved_replays = ReflectionReplayLog.objects.filter(
        assistant=assistant, new_score__gt=models.F("old_score")
    ).count()

    if acquired >= 10:
        badges.add("glossary_apprentice")
    else:
        badges.discard("glossary_apprentice")

    if reinforced >= 25:
        badges.add("semantic_master")
    else:
        badges.discard("semantic_master")

    if reflections >= 5:
        badges.add("reflection_ready")
    else:
        badges.discard("reflection_ready")

    if assistant.glossary_score >= 50:
        badges.add("vocab_proficient")
    else:
        badges.discard("vocab_proficient")

    if improved_replays >= 3:
        badges.add("replay_scholar")
    else:
        badges.discard("replay_scholar")

    if len(badges) >= 3:
        badges.add("delegation_ready")
    else:
        badges.discard("delegation_ready")

    old_badges = set(assistant.skill_badges or [])
    assistant.skill_badges = sorted(badges)
    if old_badges != badges:
        history = assistant.badge_history or []
        history.append({"badges": sorted(badges), "count": len(history) + 1})
        assistant.badge_history = history[-20:]
        assistant.save(update_fields=["skill_badges", "badge_history"])


def filter_assistants_by_badge(badges: Iterable[str]):
    """Return queryset of assistants having all given badges."""
    qs = Assistant.objects.all()
    for badge in badges:
        qs = qs.filter(skill_badges__contains=[badge])
    return qs
