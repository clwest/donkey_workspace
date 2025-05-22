from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from assistants.models.assistant import (
    Assistant,
    ChatSession,
    DelegationEvent,
    TokenUsage,
)
from assistants.models.thoughts import AssistantThoughtLog
from assistants.serializers import AssistantChatMessageSerializer
from assistants.utils.session_utils import (
    r,
    load_session_messages,
    flush_session_to_db,
)
from django.shortcuts import get_object_or_404


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

    token_usage = (
        TokenUsage.objects.filter(session=session).order_by("-created_at").first()
    )
    usage_data = (
        {
            "prompt_tokens": token_usage.prompt_tokens,
            "completion_tokens": token_usage.completion_tokens,
            "total_tokens": token_usage.total_tokens,
        }
        if token_usage
        else None
    )
    threshold = (
        session.assistant.delegation_threshold_tokens if session.assistant else None
    )
    close_to_threshold = (
        usage_data is not None
        and threshold is not None
        and usage_data["total_tokens"] >= threshold * 0.8
    )

    return Response(
        {
            "session_id": session.session_id,
            "assistant_name": session.assistant.name if session.assistant else None,
            "assistant_slug": session.assistant.slug if session.assistant else None,
            "project": session.project.title if session.project else None,
            "narrative_thread": session.narrative_thread_id,
            "created_at": session.created_at,
            "messages": message_data,
            "token_usage": usage_data,
            "delegation_threshold": threshold,
            "close_to_threshold": close_to_threshold,
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


@api_view(["GET"])
def sessions_for_assistant(request, slug):
    """Return chat sessions, memory summaries, and active threads for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    sessions = ChatSession.objects.filter(assistant=assistant).order_by("-created_at")
    session_data = [
        {
            "session_id": s.session_id,
            "created_at": s.created_at,
            "narrative_thread": s.narrative_thread_id,
            "message_count": s.messages.count(),
        }
        for s in sessions
    ]

    from memory.services import MemoryService
    from mcp_core.models import NarrativeThread
    from mcp_core.serializers_tags import NarrativeThreadSerializer

    memories = MemoryService.filter_entries(chat_session__in=sessions).exclude(
        summary__isnull=True
    )
    memory_data = [
        {
            "id": str(m.id),
            "summary": m.summary,
            "session_id": m.chat_session.session_id if m.chat_session else None,
        }
        for m in memories
    ]

    thread_ids = sessions.values_list("narrative_thread", flat=True).distinct()
    threads = NarrativeThread.objects.filter(id__in=thread_ids)
    thread_data = NarrativeThreadSerializer(threads, many=True).data

    return Response(
        {
            "sessions": session_data,
            "memory_summaries": memory_data,
            "threads": thread_data,
        }
    )


@api_view(["GET"])
def session_summary(request, slug, session_id):
    """Return thoughts and delegations ordered for this session."""
    assistant = get_object_or_404(Assistant, slug=slug)
    session = get_object_or_404(ChatSession, session_id=session_id)

    thoughts = (
        AssistantThoughtLog.objects.filter(narrative_thread=session.narrative_thread)
        .select_related("assistant")
        .order_by("created_at")
    )
    delegations = (
        DelegationEvent.objects.filter(triggering_session=session)
        .select_related("parent_assistant", "child_assistant")
        .order_by("created_at")
    )

    entries = []
    for t in thoughts:
        entries.append(
            {
                "type": "thought",
                "assistant": t.assistant.name if t.assistant else None,
                "content": t.thought,
                "feedback": t.feedback,
                "created_at": t.created_at,
            }
        )

    for d in delegations:
        entries.append(
            {
                "type": "delegation",
                "assistant": d.parent_assistant.name,
                "child": d.child_assistant.name,
                "child_slug": d.child_assistant.slug,
                "reason": d.reason,
                "summary": d.summary,
                "created_at": d.created_at,
            }
        )

    entries.sort(key=lambda x: x["created_at"])
    return Response({"entries": entries})
