from rest_framework.decorators import api_view
from rest_framework.response import Response

from assistants.models import DelegationEvent
from assistants.serializers import DelegationEventSerializer


@api_view(["GET"])
def recent_delegation_events(request):
    """Return the 10 most recent delegation events."""
    events = (
        DelegationEvent.objects.select_related(
            "parent_assistant",
            "child_assistant",
            "triggering_memory",
        ).recent_delegation_events()
    )
    serializer = DelegationEventSerializer(events, many=True)
    return Response(serializer.data)
