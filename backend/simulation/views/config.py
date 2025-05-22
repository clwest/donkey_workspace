from rest_framework import viewsets
from ..models import SimulationConfig
from ..serializers import SimulationConfigSerializer


class SimulationConfigViewSet(viewsets.ModelViewSet):
    queryset = SimulationConfig.objects.all().order_by("-created_at")
    serializer_class = SimulationConfigSerializer
