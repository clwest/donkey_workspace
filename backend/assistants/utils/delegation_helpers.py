import uuid
from typing import Optional

from assistants.models import Assistant, DelegationEvent, ChatSession
from assistants.helpers.reflection_helpers import reflect_on_delegation
from assistants.serializers import AssistantFromPromptSerializer
from prompts.models import Prompt
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread
from project.models import Project


def spawn_delegated_assistant(
    prompt: Prompt,
    parent_assistant: Assistant,
    memory_entry: Optional[MemoryEntry] = None,
    *,
    reason: str = "delegation",
    summary: Optional[str] = None,
) -> Assistant:
    """Spawn a delegate assistant based on a prompt.

    Uses ``AssistantFromPromptSerializer`` to bootstrap a new assistant from the
    given prompt. The new assistant inherits the parent's configuration and is
    linked via ``parent_assistant``. If ``memory_entry`` or its related objects
    contain a ``NarrativeThread`` it will be reused for the new assistant's
    project and chat session. A ``DelegationEvent`` is recorded linking the two
    assistants.
    """

    thread: Optional[NarrativeThread] = None
    session: Optional[ChatSession] = None

    if memory_entry:
        thread = memory_entry.narrative_thread or None
        session = memory_entry.chat_session or None
        if not thread and session:
            thread = session.thread or session.narrative_thread
        if not thread and memory_entry.related_project:
            thread = (
                memory_entry.related_project.thread
                or memory_entry.related_project.narrative_thread
            )

    data = {
        "prompt_id": str(prompt.id),
        "parent_assistant_id": str(parent_assistant.id),
    }
    if thread:
        data["parent_thread_id"] = str(thread.id)

    serializer = AssistantFromPromptSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    result = serializer.save()

    child: Assistant = result["assistant"]
    assistant_project = result["project"]
    project = Project.objects.filter(assistant_project=assistant_project).first()

    ChatSession.objects.create(
        assistant=child,
        project=project,
        narrative_thread=thread,
        thread=thread,
        session_id=uuid.uuid4(),
    )

    event = DelegationEvent.objects.create(
        parent_assistant=parent_assistant,
        child_assistant=child,
        triggering_memory=memory_entry,
        triggering_session=session,
        reason=reason,
        summary=summary,
    )

    reflect_on_delegation(event)

    return child
