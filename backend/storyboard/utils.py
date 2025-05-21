from django.utils import timezone
from datetime import timedelta

from .models import NarrativeEvent


def upcoming_events_by_scene(assistant, days=7):
    """Return upcoming events ordered by scene relevance for the assistant."""
    now = timezone.now()
    events = NarrativeEvent.objects.filter(
        start_time__gte=now,
        start_time__lte=now + timedelta(days=days),
    )
    scored = []
    for event in events:
        score = 0
        if event.scene and assistant.preferred_scene_tags:
            if event.scene in assistant.preferred_scene_tags:
                score = 1
        scored.append((score, event))
    scored.sort(key=lambda t: (-t[0], t[1].start_time or now))
    return [e for _, e in scored]
