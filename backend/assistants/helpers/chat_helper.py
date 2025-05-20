from assistants.models import ChatSession, AssistantChatMessage
from project.models import Project
from memory.models import MemoryEntry


def get_or_create_chat_session(session_id, assistant=None, project=None, thread=None):

    session, _ = ChatSession.objects.get_or_create(session_id=session_id)

    if assistant and not session.assistant:
        session.assistant = assistant

    if project and not session.project:
        session.project = project
    if assistant and not session.memory_chain and assistant.default_memory_chain:
        session.memory_chain = assistant.default_memory_chain
        if not project and not session.project:
            session.project = assistant.default_memory_chain.project

    derived_thread = None

    if thread:
        derived_thread = thread
    else:
        if session.thread:
            derived_thread = session.thread
        else:
            memory = (
                MemoryEntry.objects.filter(chat_session=session)
                .order_by("-created_at")
                .first()
            )
            if memory:
                derived_thread = memory.narrative_thread or (
                    memory.related_project.thread
                    if memory.related_project and memory.related_project.thread
                    else (
                        memory.related_project.narrative_thread
                        if memory.related_project
                        else None
                    )
                )

        if not derived_thread and (
            project or assistant and getattr(assistant, "current_project", None)
        ):
            proj = project or assistant.current_project
            if proj:
                derived_thread = proj.thread or proj.narrative_thread

    if derived_thread:
        session.thread = derived_thread
        if not session.narrative_thread:
            session.narrative_thread = derived_thread

    session.save()
    return session


def save_chat_message(
    session,
    role,
    content,
    message_uuid=None,
    memory=None,
    **extra_fields,
):
    return AssistantChatMessage.objects.create(
        session=session,
        role=role,
        content=content,
        uuid=message_uuid,
        memory=memory,
        **extra_fields,
    )
