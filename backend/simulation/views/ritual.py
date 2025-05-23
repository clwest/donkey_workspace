from rest_framework import viewsets
from ..models import RitualInteractionEvent
from ..serializers import RitualInteractionEventSerializer


class RitualInteractionEventViewSet(viewsets.ModelViewSet):
    queryset = RitualInteractionEvent.objects.all().order_by("-created_at")
    serializer_class = RitualInteractionEventSerializer
