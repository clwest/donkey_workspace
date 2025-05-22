from assistants.models.thoughts import AssistantThoughtLog
from memory.models import MemoryEntry

def generate_task_from_memory(memory: MemoryEntry) -> dict:
    """Return basic task suggestion from a memory entry."""
    title = memory.summary or memory.event[:50]
    notes = memory.event
    return {"title": title, "notes": notes}


def generate_task_from_thought(thought: AssistantThoughtLog) -> dict:
    """Return basic task suggestion from a thought."""
    title = thought.thought[:80]
    notes = thought.thought
    return {"title": title, "notes": notes}
