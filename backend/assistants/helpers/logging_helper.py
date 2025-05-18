from assistants.models import AssistantThoughtLog


def log_assistant_thought(
    assistant,
    thought: str,
    trace: str = "",
    linked_memory=None,
    project=None,
    thought_type: str = "generated",
):
    """
    Save a thought from or about the assistant to the AssistantThoughtLog.
    """
    return AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=thought,
        thought_trace=trace or "",
        linked_memory=linked_memory,
        project=project,
        thought_type=thought_type,
    )
