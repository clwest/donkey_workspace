from rest_framework.decorators import api_view
from rest_framework.response import Response

from assistants.models.assistant import RoutingSuggestionLog
from assistants.serializers import RoutingSuggestionLogSerializer


@api_view(["GET"])
def routing_history(request):
    """Return recent routing suggestion logs."""
    slug = request.GET.get("assistant")
    logs = RoutingSuggestionLog.objects.all()
    if slug:
        logs = logs.filter(suggested_assistant__slug=slug)
    logs = logs.order_by("-timestamp")[:25]
    serializer = RoutingSuggestionLogSerializer(logs, many=True)
    return Response({"results": serializer.data})
