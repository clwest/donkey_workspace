from rest_framework import viewsets
from ..models import SimulationStateTracker
from ..serializers import SimulationStateTrackerSerializer


class SimulationStateTrackerViewSet(viewsets.ModelViewSet):
    queryset = SimulationStateTracker.objects.all().order_by("-created_at")
    serializer_class = SimulationStateTrackerSerializer
