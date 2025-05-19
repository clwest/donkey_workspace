from rest_framework.decorators import api_view
from rest_framework.response import Response

from assistants.models import DelegationEvent
from assistants.serializers import DelegationEventSerializer
from assistants.utils.delegation import (
    spawn_delegated_assistant,
    should_delegate,
)
from assistants.models import Assistant, TokenUsage, ChatSession
from memory.models import MemoryEntry


@api_view(["GET"])
def recent_delegation_events(request):
    """Return the 10 most recent delegation events."""
    events = DelegationEvent.objects.select_related(
        "parent_assistant",
        "child_assistant",
        "triggering_memory",
    ).recent_delegation_events()
    serializer = DelegationEventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def delegation_events_for_assistant(request, slug):
    """List delegation events where the assistant was parent or child."""
    from django.db.models import Q
    from assistants.models import Assistant

    assistant = Assistant.objects.filter(slug=slug).first()
    if not assistant:
        return Response({"error": "Assistant not found"}, status=404)

    events = (
        DelegationEvent.objects.select_related(
            "parent_assistant",
            "child_assistant",
            "triggering_memory",
            "triggering_session",
        )
        .filter(Q(parent_assistant=assistant) | Q(child_assistant=assistant))
        .order_by("-created_at")
    )
    serializer = DelegationEventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def primary_delegations(request):
    """List delegation events involving the primary assistant."""
    from django.db.models import Q
    from assistants.models import Assistant

    primary = Assistant.objects.filter(is_primary=True).first()
    if not primary:
        return Response({"error": "No primary assistant."}, status=404)

    events = (
        DelegationEvent.objects.select_related(
            "parent_assistant",
            "child_assistant",
            "triggering_memory",
            "triggering_session",
        )
        .filter(Q(parent_assistant=primary) | Q(child_assistant=primary))
        .order_by("-created_at")
    )
    serializer = DelegationEventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def delegation_trace(request, slug):
    """Return a nested delegation tree starting from this assistant."""
    from assistants.models import Assistant

    def build_trace(assistant):
        events = (
            DelegationEvent.objects.select_related(
                "child_assistant",
                "triggering_session",
            )
            .filter(parent_assistant=assistant)
            .order_by("created_at")
        )
        trace = []
        for e in events:
            trace.append(
                {
                    "child": e.child_assistant.name,
                    "child_slug": e.child_assistant.slug,
                    "reason": e.reason,
                    "summary": e.summary,
                    "session_id": (
                        str(e.triggering_session.session_id)
                        if e.triggering_session
                        else None
                    ),
                    "created_at": e.created_at,
                    "delegations": build_trace(e.child_assistant),
                }
            )
        return trace

    assistant = Assistant.objects.filter(slug=slug).first()
    if not assistant:
        return Response({"error": "Assistant not found"}, status=404)
    data = build_trace(assistant)
    return Response(data)


@api_view(["POST"])
def evaluate_delegation(request, slug):
    """Return whether delegation should occur for this session."""
    assistant = Assistant.objects.filter(slug=slug).first()
    if not assistant:
        return Response({"error": "Assistant not found"}, status=404)

    session_id = request.data.get("session_id")
    feedback_flag = request.data.get("feedback_flag")
    token_count = int(request.data.get("token_count") or 0)

    chat_session = (
        ChatSession.objects.filter(session_id=session_id).first()
        if session_id
        else None
    )
    if chat_session:
        token_usage, _ = TokenUsage.objects.get_or_create(
            session=chat_session,
            defaults={"assistant": assistant, "usage_type": "chat"},
        )
        token_usage.total_tokens = token_count or token_usage.total_tokens
    else:
        token_usage = TokenUsage(total_tokens=token_count)

    if should_delegate(assistant, token_usage, feedback_flag):
        existing = (
            Assistant.objects.filter(specialty=assistant.specialty, is_active=True)
            .exclude(id=assistant.id)
            .first()
        )
        if existing:
            return Response({"should_delegate": True, "suggested_agent": existing.slug})

        recent_memory = None
        if chat_session:
            recent_memory = (
                MemoryEntry.objects.filter(chat_session=chat_session)
                .order_by("-created_at")
                .first()
            )
            new_agent = spawn_delegated_assistant(
                chat_session, memory_entry=recent_memory
            )
        else:
            new_agent = spawn_delegated_assistant(assistant)

        return Response({"should_delegate": True, "suggested_agent": new_agent.slug})

    return Response({"should_delegate": False, "suggested_agent": None})
