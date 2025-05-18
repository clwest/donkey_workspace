from rest_framework.decorators import api_view
from rest_framework.response import Response

from assistants.models import DelegationEvent
from assistants.serializers import DelegationEventSerializer


@api_view(["GET"])
def recent_delegation_events(request):
    """Return the 25 most recent delegation events."""
    events = (
        DelegationEvent.objects.select_related(
            "parent_assistant",
            "child_assistant",
            "triggering_memory",
            "triggering_session",
        )
        .order_by("-created_at")[:25]
    )
    serializer = DelegationEventSerializer(events, many=True)
    return Response(serializer.data)
