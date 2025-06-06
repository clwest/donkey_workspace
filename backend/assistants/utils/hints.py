from django.utils import timezone
from assistants.models import AssistantHintState


def record_hint_seen(user, assistant, hint_id: str) -> AssistantHintState:
    """Mark a hint as seen for the given user and assistant."""
    obj, _ = AssistantHintState.objects.get_or_create(
        user=user, assistant=assistant, hint_id=hint_id
    )
    obj.seen_at = timezone.now()
    if obj.dismissed:
        obj.dismissed = False
    obj.save()
    return obj
