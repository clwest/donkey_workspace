from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from assistants.models import ChatSession
from assistants.serializers import AssistantChatMessageSerializer
from assistants.utils.assistant_session import load_session_messages
from assistants.models import Assistant
from django.shortcuts import get_object_or_404
from assistants.helpers.redis_helpers import r
from assistants.utils.assistant_session import flush_session_to_db


@api_view(["GET"])
def list_chat_sessions(request):
    queryset = ChatSession.objects.all().order_by("-created_at")
    assistant_slug = request.query_params.get("assistant")
    if assistant_slug:
        queryset = queryset.filter(assistant__slug=assistant_slug)

    sessions_data = []
    for session in queryset:
        sessions_data.append(
            {
                "session_id": session.session_id,
                "assistant_name": session.assistant.name if session.assistant else None,
                "assistant_slug": session.assistant.slug if session.assistant else None,
                "narrative_thread": session.narrative_thread_id,
                "created_at": session.created_at,
                "message_count": session.messages.count(),
            }
        )

    return Response(sessions_data)


@api_view(["GET"])
def chat_session_detail(request, session_id):
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return Response({"error": "Session not found."}, status=404)

    messages = session.messages.order_by("created_at").all()
    message_data = AssistantChatMessageSerializer(
        messages, many=True
    ).data  # Make sure this serializer exists

    return Response(
        {
            "session_id": session.session_id,
            "assistant_name": session.assistant.name if session.assistant else None,
            "project": session.project.title if session.project else None,
            "narrative_thread": session.narrative_thread_id,
            "created_at": session.created_at,
            "messages": message_data,
        }
    )


@api_view(["GET"])
def get_chat_session_messages(request, slug, session_id):
    assistant = get_object_or_404(Assistant, slug=slug)
    messages = load_session_messages(session_id)
    return Response(
        {"assistant": assistant.name, "session_id": session_id, "messages": messages}
    )


# @api_view(["POST"])
# def flush_all_sessions(request):
#     count = 0
#     for key in r.scan_iter("chat:*"):
#         session_id = key.decode().split("chat:")[-1]
#         count += flush_session_to_db(session_id)
#     return Response({"flushed_count": count})
