from assistants.models import ChatSession, AssistantChatMessage
from project.models import Project


def get_or_create_chat_session(session_id, assistant=None, project=None, thread=None):

    session, _ = ChatSession.objects.get_or_create(session_id=session_id)

    if assistant and not session.assistant:
        session.assistant = assistant

    if project and not session.project:
        session.project = project

    if thread:
        session.thread = thread
        if not session.narrative_thread:
            session.narrative_thread = thread

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
