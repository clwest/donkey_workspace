from typing import Iterable
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from assistants.models.reflection import AssistantReflectionLog


def update_assistant_badges(assistant: Assistant) -> None:
    """Update skill_badges on the given assistant."""
    badges = set(assistant.skill_badges or [])

    acquired = SymbolicMemoryAnchor.objects.filter(assistant=assistant).count()
    reinforced = SymbolicMemoryAnchor.objects.filter(reinforced_by=assistant).count()
    reflections = AssistantReflectionLog.objects.filter(assistant=assistant).count()

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

    if len(badges) >= 3:
        badges.add("delegation_ready")
    else:
        badges.discard("delegation_ready")

    assistant.skill_badges = sorted(badges)
    assistant.save(update_fields=["skill_badges"])


def filter_assistants_by_badge(badges: Iterable[str]):
    """Return queryset of assistants having all given badges."""
    qs = Assistant.objects.all()
    for badge in badges:
        qs = qs.filter(skill_badges__contains=[badge])
    return qs
