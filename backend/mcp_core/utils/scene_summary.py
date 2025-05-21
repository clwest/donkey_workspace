from datetime import timedelta
from assistants.models import AssistantThoughtLog, DelegationEvent
from memory.models import MemoryEntry
from story.models import NarrativeEvent
from utils.llm_router import call_llm


def summarize_scene_context(event: NarrativeEvent) -> str:
    """Generate and store a summary for a narrative event."""
    # Collect thoughts linked directly to the event
    thoughts = AssistantThoughtLog.objects.filter(linked_event=event).order_by("created_at")

    # Collect memories and delegations near the event timestamp
    start = event.timestamp - timedelta(hours=1)
    end = event.timestamp + timedelta(hours=1)

    memories = MemoryEntry.objects.filter(timestamp__gte=start, timestamp__lte=end)
    delegations = DelegationEvent.objects.filter(created_at__gte=start, created_at__lte=end)

    entries = []
    for t in thoughts:
        mood = f" ({t.mood})" if t.mood else ""
        entries.append(f"THOUGHT{mood}: {t.thought}")

    for d in delegations:
        entries.append(
            f"DELEGATION: {d.parent_assistant.name} -> {d.child_assistant.name} reason={d.reason}"
        )

    for m in memories:
        emotion = f" ({m.emotion})" if m.emotion else ""
        entries.append(f"MEMORY{emotion}: {m.event}")

    joined = "\n".join(entries)
    prompt = (
        "Summarize this narrative scene. Highlight assistant thoughts, actions, emotions, and any delegation decisions.\n\n"  # noqa: E501
        f"Scene Content:\n{joined}"
    )

    summary = call_llm([{"role": "user", "content": prompt}])
    event.scene_summary = summary
    event.summary_generated = True
    event.save(update_fields=["scene_summary", "summary_generated"])
    return summary
