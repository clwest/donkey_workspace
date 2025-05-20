from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from assistants.models import (
    Assistant,
    ChatSession,
    AssistantThoughtLog,
    AssistantSwitchEvent,
)
from assistants.serializers import AssistantSwitchEventSerializer
from assistants.utils.assistant_switching import suggest_assistant_switch


@api_view(["POST"])
def suggest_switch(request):
    """Return a suggested assistant for this session."""
    session_id = request.data.get("session_id")
    if not session_id:
        return Response({"error": "session_id required"}, status=400)

    session = get_object_or_404(ChatSession, session_id=session_id)
    suggestion = suggest_assistant_switch(session)
    if not suggestion:
        return Response({"suggested_assistant": None})

    data = {
        "name": suggestion["assistant"].name,
        "slug": suggestion["assistant"].slug,
        "reason": suggestion["reason"],
        "confidence": suggestion["confidence"],
    }
    return Response({"suggested_assistant": data})


@api_view(["POST"])
def switch_session(request):
    """Switch a chat session to another assistant, preserving thread."""
    session_id = request.data.get("session_id")
    to_slug = request.data.get("assistant_slug")
    automated = bool(request.data.get("automated", False))
    reason = request.data.get("reason", "switch")
    if not session_id or not to_slug:
        return Response({"error": "session_id and assistant_slug required"}, status=400)

    from_session = get_object_or_404(ChatSession, session_id=session_id)
    to_assistant = get_object_or_404(Assistant, slug=to_slug)

    if from_session.ended_at is None:
        from_session.ended_at = timezone.now()
        from_session.save()

    thread = from_session.narrative_thread or from_session.thread
    new_session = ChatSession.objects.create(
        assistant=to_assistant,
        project=to_assistant.current_project,
        narrative_thread=thread,
        thread=thread,
        session_id=uuid.uuid4(),
    )

    AssistantThoughtLog.objects.create(
        assistant=from_session.assistant,
        thought=f"Session switched to {to_assistant.name}",
        narrative_thread=thread,
    )

    event = AssistantSwitchEvent.objects.create(
        from_assistant=from_session.assistant,
        to_assistant=to_assistant,
        from_session=from_session,
        to_session=new_session,
        narrative_thread=thread,
        reason=reason,
        automated=automated,
    )

    serializer = AssistantSwitchEventSerializer(event)
    return Response(
        {"new_session_id": str(new_session.session_id), "event": serializer.data}
    )
