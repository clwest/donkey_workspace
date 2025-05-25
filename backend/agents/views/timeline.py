from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models.orchestration import AssistantOrchestrationEvent
from ..serializers import AssistantOrchestrationEventSerializer


@api_view(["GET"])
def orchestration_timeline(request):
    events = AssistantOrchestrationEvent.objects.all().order_by("-started_at")[:50]
    serializer = AssistantOrchestrationEventSerializer(events, many=True)
    return Response(serializer.data)
