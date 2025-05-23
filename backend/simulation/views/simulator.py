from rest_framework import viewsets
from ..models import MythScenarioSimulator
from ..serializers import MythScenarioSimulatorSerializer


class MythScenarioSimulatorViewSet(viewsets.ModelViewSet):
    queryset = MythScenarioSimulator.objects.all().order_by("-created_at")
    serializer_class = MythScenarioSimulatorSerializer
