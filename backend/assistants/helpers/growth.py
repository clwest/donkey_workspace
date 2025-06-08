from django.utils import timezone
from assistants.growth_rules import GROWTH_RULES
from assistants.helpers.logging_helper import log_trail_marker
from memory.models import MemoryEntry
from memory.memory_service import get_memory_service
from assistants.models.reflection import AssistantReflectionLog


def upgrade_growth_stage(assistant) -> bool:
    """Increment the assistant's growth stage if points meet the threshold."""
    next_stage = assistant.growth_stage + 1
    rule = GROWTH_RULES.get(next_stage)
    if not rule:
        return False
    if assistant.growth_points < rule["threshold"]:
        return False
    assistant.growth_stage = next_stage
    assistant.growth_unlocked_at = timezone.now()
    assistant.save(update_fields=["growth_stage", "growth_unlocked_at"])
    summary = (
        f"Reached Stage {next_stage} ({rule['label']}). "
        + ("Unlocked: " + ", ".join(rule.get("unlocks", [])) if rule.get("unlocks") else "")
    )
    mem = MemoryEntry.objects.create(
        assistant=assistant,
        context=assistant.memory_context,
        summary=summary,
        event=summary,
        type="growth_summary",
        is_summary=True,
        memory_type="milestone",
    )
    assistant.growth_summary_memory = mem
    assistant.save(update_fields=["growth_summary_memory"])
    get_memory_service().log_reflection(summary, [mem])
    AssistantReflectionLog.objects.create(
        assistant=assistant,
        summary=summary,
        title=f"Stage {next_stage} Unlock",
        linked_memory=mem,
        category="meta",
    )
    log_trail_marker(assistant, "level_up", mem)
    return True
