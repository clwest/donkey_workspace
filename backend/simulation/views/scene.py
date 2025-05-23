from rest_framework import viewsets
from ..models import SceneControlEngine
from ..serializers import SceneControlEngineSerializer


class SceneControlEngineViewSet(viewsets.ModelViewSet):
    queryset = SceneControlEngine.objects.all().order_by("-last_updated")
    serializer_class = SceneControlEngineSerializer
