from rest_framework import viewsets
from ..models import BeliefNarrativeEngineInstance
from ..serializers import BeliefNarrativeEngineInstanceSerializer


class BeliefNarrativeEngineInstanceViewSet(viewsets.ModelViewSet):
    queryset = BeliefNarrativeEngineInstance.objects.all().order_by("-created_at")
    serializer_class = BeliefNarrativeEngineInstanceSerializer
