from rest_framework.decorators import api_view
from rest_framework.response import Response

from assistants.models import DelegationEvent
from assistants.serializers import DelegationEventSerializer


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
