from assistants.models import AssistantThoughtLog
from .mood import detect_mood, update_mood_stability


def log_assistant_thought(
    assistant,
    thought: str,
    trace: str = "",
    linked_memory=None,
    linked_memories=None,
    linked_reflection=None,
    linked_event=None,
    project=None,
    thought_type: str = "generated",
    bookmark_label: str | None = None,
):
    """
    Save a thought from or about the assistant to the AssistantThoughtLog.
    """
    mood = detect_mood(thought)
    log = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=thought,
        thought_trace=trace or "",
        linked_memory=linked_memory,
        linked_reflection=linked_reflection,
        linked_event=linked_event,
        project=project,
        thought_type=thought_type,
        mood=mood,
        mood_snapshot={"mood": mood, "stability": assistant.mood_stability_index},
    )
    if linked_memories:
        log.linked_memories.set(linked_memories)
    update_mood_stability(assistant, mood)
    if bookmark_label and linked_memory:
        linked_memory.is_bookmarked = True
        linked_memory.bookmark_label = bookmark_label
        linked_memory.save()
    return log
