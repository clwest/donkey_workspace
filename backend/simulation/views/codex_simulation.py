from rest_framework import viewsets
from ..models import CodexSimulationScenario
from ..serializers import CodexSimulationScenarioSerializer


class CodexSimulationScenarioViewSet(viewsets.ModelViewSet):
    queryset = CodexSimulationScenario.objects.all().order_by("-created_at")
    serializer_class = CodexSimulationScenarioSerializer
