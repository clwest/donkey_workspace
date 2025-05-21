from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import NarrativeEvent
from .serializers import NarrativeEventSerializer
from .utils import upcoming_events_by_scene


class NarrativeEventViewSet(viewsets.ModelViewSet):
    queryset = NarrativeEvent.objects.all().order_by('order', 'created_at')
    serializer_class = NarrativeEventSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, url_path="relevant/(?P<assistant_slug>[^/]+)")
    def relevant_for_assistant(self, request, assistant_slug=None):
        from assistants.models import Assistant

        try:
            assistant = Assistant.objects.get(slug=assistant_slug)
        except Assistant.DoesNotExist:
            return Response([], status=404)

        events = upcoming_events_by_scene(assistant)
        data = NarrativeEventSerializer(events, many=True).data
        return Response(data)
