from rest_framework import viewsets
from ..models import PurposeLoopCinematicEngine
from ..serializers import PurposeLoopCinematicEngineSerializer


class PurposeLoopCinematicEngineViewSet(viewsets.ModelViewSet):
    queryset = PurposeLoopCinematicEngine.objects.all().order_by("-created_at")
    serializer_class = PurposeLoopCinematicEngineSerializer
