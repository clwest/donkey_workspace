from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType

from .models import NarrativeEvent
from assistants.utils.delegation import spawn_delegated_assistant
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from assistants.models import AssistantThoughtLog
from mcp_core.models import MemoryContext


@shared_task
def evaluate_narrative_triggers():
    """Evaluate narrative events and trigger assistant actions."""
    now = timezone.now()
    upcoming = now + timedelta(days=1)
    recent = now - timedelta(days=1)

    events = NarrativeEvent.objects.filter(
        start_time__lte=upcoming,
        end_time__gte=recent,
    ).select_related("linked_assistant")

    for event in events:
        assistant = event.linked_assistant
        if not assistant:
            continue

        if event.last_triggered and (now - event.last_triggered) < timedelta(minutes=5):
            continue

        # Upcoming
        if event.start_time and event.start_time > now and event.auto_delegate:
            if event.scene and assistant.preferred_scene_tags:
                if event.scene not in assistant.preferred_scene_tags:
                    continue
            spawn_delegated_assistant(
                assistant,
                narrative_thread=event.narrative_thread,
                reason="timeline_trigger",
                summary=f"Triggered by {event.title}",
            )
            event.last_triggered = now
            event.save(update_fields=["last_triggered"])
            continue

        # Ongoing
        within_event = (
            event.start_time and event.end_time and event.start_time <= now <= event.end_time
        )
        if within_event and event.auto_reflect:
            context = MemoryContext.objects.create(
                content=f"Reflection triggered by event {event.title}",
                target_content_type=ContentType.objects.get_for_model(NarrativeEvent),
                target_object_id=event.id,
            )
            engine = AssistantReflectionEngine(assistant)
            engine.reflect_now(context)
            event.last_triggered = now
            event.save(update_fields=["last_triggered"])

        # Recently ended
        if event.end_time and event.end_time < now <= event.end_time + timedelta(days=1):
            if event.auto_summarize:
                AssistantThoughtLog.objects.create(
                    assistant=assistant,
                    thought=f"Summary for event {event.title}",
                    thought_type="timeline_trigger",
                    origin="automatic",
                    linked_event=event,
                )
                event.last_triggered = now
                event.save(update_fields=["last_triggered"])
