from assistants.models import AssistantThoughtLog
from .mood import detect_mood


def log_assistant_thought(
    assistant,
    thought: str,
    trace: str = "",
    linked_memory=None,
    linked_memories=None,
    linked_reflection=None,
    project=None,
    thought_type: str = "generated",
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
        project=project,
        thought_type=thought_type,
        mood=mood,
    )
    if linked_memories:
        log.linked_memories.set(linked_memories)
    return log
