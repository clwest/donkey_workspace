from rest_framework.decorators import api_view
from rest_framework.response import Response

from assistants.models.thoughts import AssistantThoughtLog
from assistants.serializers_pass import (
    DelegationEventSerializer,
    RecentDelegationEventSerializer,
    DelegationTraceSerializer,
)
from assistants.utils.delegation import (
    spawn_delegated_assistant,
    should_delegate,
)
from assistants.models.assistant import (
    Assistant,
    TokenUsage,
    ChatSession,
    AssistantChatMessage,
    DelegationEvent,
)
from assistants.utils.delegation_helpers import get_trust_score
from memory.services import MemoryService
from memory.serializers import MemoryEntrySerializer
from assistants.utils.delegation_trace import build_delegation_trace
from django.utils import timezone


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
def recent_delegations(request):
    """Return a brief list of the 10 most recent delegations."""
    events = DelegationEvent.objects.select_related(
        "parent_assistant",
        "child_assistant",
    ).recent_delegation_events()
    serializer = RecentDelegationEventSerializer(events, many=True)
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
                    "assistant_slug": assistant.slug,
                    "delegated_to_slug": e.child_assistant.slug,
                    "delegated_to": e.child_assistant.name,
                    "reason": e.reason,
                    "summary": e.summary,
                    "session_id": (
                        str(e.triggering_session.session_id)
                        if e.triggering_session
                        else None
                    ),
                    "delegation_event_id": str(e.id),
                    "created_at": e.created_at,
                    "delegations": build_trace(e.child_assistant),
                }
            )
        return trace

    assistant = Assistant.objects.filter(slug=slug).first()
    if not assistant:
        return Response({"error": "Assistant not found"}, status=404)
    data = build_trace(assistant)
    serializer = DelegationTraceSerializer(data, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def hierarchical_memory(request, slug):
    """Return memory entries across a delegation chain with depth info."""
    assistant = Assistant.objects.filter(slug=slug).first()
    if not assistant:
        return Response({"error": "Assistant not found"}, status=404)

    entries = build_delegation_trace(assistant)
    serializer = MemoryEntrySerializer(entries, many=True)
    data = serializer.data
    for idx, entry in enumerate(entries):
        data[idx]["depth"] = getattr(entry, "depth", 0)
        data[idx]["delegation_event_id"] = (
            str(entry.delegation_event_id)
            if getattr(entry, "delegation_event_id", None)
            else None
        )
        data[idx]["assistant"] = entry.assistant_name
        data[idx]["parent"] = entry.parent_assistant_name
        data[idx]["assistant_id"] = str(entry.assistant_id)
        data[idx]["is_delegated"] = entry.is_delegated
        if entry.document_id:
            data[idx]["linked_document"] = (
                entry.document.title if entry.document else None
            )
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
                MemoryService.filter_entries(chat_session=chat_session)
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


@api_view(["POST"])
def suggest_delegation(request, slug):
    """Suggest an assistant to delegate a memory or objective."""
    assistant = Assistant.objects.filter(slug=slug).first()
    if not assistant:
        return Response({"error": "Assistant not found"}, status=404)

    ctx_type = request.data.get("context_type")
    ctx_id = request.data.get("context_id")
    context = None
    if ctx_type == "memory":
        context = MemoryService.get_entry(ctx_id)
    elif ctx_type == "objective":
        from assistants.models import AssistantObjective

        context = AssistantObjective.objects.filter(id=ctx_id).first()
    if context is None:
        return Response({"error": "Context not found"}, status=404)

    from assistants.utils.recommendation_engine import suggest_agent_for_task

    suggestion = suggest_agent_for_task(assistant, context)
    if not suggestion:
        return Response(
            {"recommended_assistant": None, "message": "No suitable assistant found"}
        )

    rec = Assistant.objects.get(id=suggestion["assistant_id"])
    resp = {
        "name": rec.name,
        "slug": rec.slug,
        "score": suggestion.get("score"),
        "reason": suggestion.get("match_reason"),
        "adjusted_for_trust": suggestion.get("adjusted_for_trust"),
        "recent_failures": suggestion.get("recent_failures"),
    }
    trust = get_trust_score(rec)
    if trust.get("overall_label"):
        resp["trust_label"] = trust["overall_label"]

    return Response({"recommended_assistant": resp})


@api_view(["POST"])
def handoff_session(request, slug):
    """Transfer an active session to another assistant."""
    parent = Assistant.objects.filter(slug=slug).first()
    if not parent:
        return Response({"error": "Assistant not found"}, status=404)

    target_slug = request.data.get("target_slug")
    if not target_slug:
        return Response({"error": "target_slug required"}, status=400)
    target = Assistant.objects.filter(slug=target_slug).first()
    if not target:
        return Response({"error": "Target assistant not found"}, status=404)

    session_id = request.data.get("session_id")
    session = ChatSession.objects.filter(session_id=session_id).first()
    if not session:
        return Response({"error": "Session not found"}, status=404)

    context_id = request.data.get("context_id")
    memory = MemoryService.get_entry(context_id) if context_id else None
    reason = request.data.get("reason", "handoff")
    end_session = bool(request.data.get("end_session"))

    DelegationEvent.objects.create(
        parent_assistant=parent,
        child_assistant=target,
        triggering_session=session,
        triggering_memory=memory,
        reason=reason,
        handoff=True,
    )

    if end_session:
        session.ended_at = timezone.now()

    session.assistant = target
    session.save()

    message = f"Conversation transferred to {target.name} due to: {reason}."
    AssistantChatMessage.objects.create(
        session=session,
        role="assistant",
        content=message,
        message_type="system",
    )

    AssistantThoughtLog.objects.create(
        assistant=parent,
        thought=message,
        thought_type="handoff",
        narrative_thread=session.narrative_thread,
    )
    AssistantThoughtLog.objects.create(
        assistant=target,
        thought=f"Resumed session from {parent.name}",
        thought_type="resumed_session",
        narrative_thread=session.narrative_thread,
    )

    return Response({"new_assistant": target.slug})


@api_view(["GET"])
def subagent_reflect(request, slug, trace_id):
    """Return reflection on a delegated assistant's output."""
    parent = get_object_or_404(Assistant, slug=slug)
    event = get_object_or_404(DelegationEvent, id=trace_id)
    child = event.child_assistant

    thoughts = list(
        AssistantThoughtLog.objects.filter(assistant=child).order_by("-created_at")[:5]
    )
    if not thoughts:
        return Response({"summary": "No sub-agent output found."})

    summary = " | ".join(t.thought[:50] for t in thoughts)

    return Response(
        {
            "summary": summary,
            "linked_thoughts": [t.thought for t in thoughts],
        }
    )
