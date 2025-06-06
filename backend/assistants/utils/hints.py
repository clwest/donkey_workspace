from django.utils import timezone
from assistants.models import AssistantHintState
from assistants.hint_config import HINTS


def record_hint_seen(user, assistant, hint_id: str) -> AssistantHintState:
    """Mark a hint as seen for the given user and assistant."""
    obj, _ = AssistantHintState.objects.get_or_create(
        user=user, assistant=assistant, hint_id=hint_id
    )
    obj.seen_at = timezone.now()
    if obj.sequence_index is None:
        try:
            obj.sequence_index = next(
                i for i, h in enumerate(HINTS) if h["id"] == hint_id
            )
        except StopIteration:
            obj.sequence_index = 0
    if obj.dismissed:
        obj.dismissed = False
    obj.save()
    return obj


def get_next_hint_for_user(assistant, user) -> str | None:
    """Return the next unfinished hint id for the user."""
    states = AssistantHintState.objects.filter(user=user, assistant=assistant)
    completed = {s.hint_id for s in states if s.completed_at}
    for h in HINTS:
        if h["id"] not in completed:
            return h["id"]
    return None
