from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import NarrativeEvent
from .serializers import NarrativeEventSerializer


class NarrativeEventViewSet(viewsets.ModelViewSet):
    queryset = NarrativeEvent.objects.all().order_by('order', 'created_at')
    serializer_class = NarrativeEventSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()
