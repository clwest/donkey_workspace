from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models

from assistants.models.assistant import (
    Assistant,
    ChatSession,
    SessionHandoff,
    AssistantChatMessage,

    AssistantHandoffLog,
)
from assistants.models.project import AssistantProject
from assistants.serializers_pass import (
    SessionHandoffSerializer,
    AssistantHandoffLogSerializer,
)
from assistants.utils.handoff import generate_handoff_summary


@api_view(["POST"])
def create_handoff(request):
    """Create a session handoff and return summary."""
    from_slug = request.data.get("from")
    to_slug = request.data.get("to")
    session_id = request.data.get("session_id")
    reason = request.data.get("reason", "handoff")
    message_id = request.data.get("triggering_message")

    from_asst = get_object_or_404(Assistant, slug=from_slug)
    to_asst = get_object_or_404(Assistant, slug=to_slug)
    session = get_object_or_404(ChatSession, session_id=session_id)

    message = None
    if message_id:
        message = AssistantChatMessage.objects.filter(uuid=message_id).first()

    summary = generate_handoff_summary(session)

    handoff = SessionHandoff.objects.create(
        from_assistant=from_asst,
        to_assistant=to_asst,
        session=session,
        reason=reason,
        triggering_message=message,
        handoff_summary=summary,
    )

    data = SessionHandoffSerializer(handoff).data
    return Response(data, status=201)


@api_view(["GET"])
def list_handoffs(request, session_id):
    """List past handoffs for a session."""
    session = get_object_or_404(ChatSession, session_id=session_id)
    qs = SessionHandoff.objects.filter(session=session).order_by("-created_at")
    data = SessionHandoffSerializer(qs, many=True).data
    return Response(data)


@api_view(["POST"])
def create_handoff_log(request):
    """Create an AssistantHandoffLog record."""
    from_slug = request.data.get("from")
    to_slug = request.data.get("to")
    project_id = request.data.get("project")
    summary = request.data.get("summary", "")

    from_asst = get_object_or_404(Assistant, slug=from_slug)
    to_asst = get_object_or_404(Assistant, slug=to_slug)
    project = None
    if project_id:
        project = AssistantProject.objects.filter(id=project_id).first()

    log = AssistantHandoffLog.objects.create(
        from_assistant=from_asst,
        to_assistant=to_asst,
        project=project,
        summary=summary,
    )
    return Response(AssistantHandoffLogSerializer(log).data, status=201)


@api_view(["GET"])
def list_handoff_logs(request, slug):
    """List AssistantHandoffLogs for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    qs = AssistantHandoffLog.objects.filter(
        models.Q(from_assistant=assistant) | models.Q(to_assistant=assistant)
    ).order_by("-created_at")
    data = AssistantHandoffLogSerializer(qs, many=True).data
    return Response(data)
