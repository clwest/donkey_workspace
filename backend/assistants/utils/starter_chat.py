import random
from assistants.helpers.memory_helpers import create_memory_from_chat
from mcp_core.models import Tag

EXCHANGES = [
    ("Hi there!", "Hello! I'm here to help you explore MythOS."),
    ("What can you do?", "I can manage projects and reflect on your tasks."),
    ("Great", "Let's get started together!")
]


def seed_chat_starter_memory(assistant, session_id="starter-demo"):
    """Seed basic chat memories for an assistant."""
    created = []
    tag, _ = Tag.objects.get_or_create(slug="starter-chat", defaults={"name": "starter-chat"})
    pairs = random.randint(1, 3)
    for i in range(pairs):
        user_msg, assistant_msg = EXCHANGES[i]
        memory = create_memory_from_chat(
            assistant_name=assistant.name,
            session_id=session_id,
            messages=[{"role": "user", "content": user_msg}],
            reply=assistant_msg,
            assistant=assistant,
            is_demo=assistant.is_demo,
        )
        memory.tags.add(tag)
        created.append(memory)
    return created


def reset_demo_memory(assistant):
    """Reset demo assistant memories and reseed starter chat."""
from memory.models import MemoryEntry
from assistants.models.reflection import AssistantReflectionLog

    if not assistant.is_demo:
        raise ValueError("Not a demo assistant")

    MemoryEntry.objects.filter(assistant=assistant).delete()
    AssistantReflectionLog.objects.filter(assistant=assistant).delete()
    return seed_chat_starter_memory(assistant)
