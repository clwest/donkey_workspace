from rest_framework import viewsets
from ..models import RitualDriftObservation
from ..serializers import RitualDriftObservationSerializer


class RitualDriftObservationViewSet(viewsets.ModelViewSet):
    queryset = RitualDriftObservation.objects.all().order_by("-observed_at")
    serializer_class = RitualDriftObservationSerializer
