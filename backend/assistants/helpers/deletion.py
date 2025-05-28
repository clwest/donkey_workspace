from assistants.models.assistant import Assistant
from project.models import Project
from memory.models import MemoryEntry


def cascade_delete_assistant(assistant: Assistant) -> None:
    """Recursively delete assistant and all of its children."""
    for child in list(assistant.sub_assistants.all()):
        cascade_delete_assistant(child)

    # Clean related objects
    Project.objects.filter(assistant=assistant).delete()
    from assistants.models.assistant import ChatSession

    ChatSession.objects.filter(assistant=assistant).delete()
    MemoryEntry.objects.filter(assistant=assistant).update(assistant=None)
    MemoryEntry.objects.filter(chat_session__assistant=assistant).update(chat_session=None)
    assistant.delete()
