from django.utils import timezone
from assistants.growth_rules import GROWTH_RULES
from assistants.helpers.logging_helper import log_trail_marker


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
    log_trail_marker(assistant, "level_up")
    return True
