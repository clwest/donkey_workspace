from rest_framework import viewsets
from ..models import MemoryCinematicFragment
from ..serializers import MemoryCinematicFragmentSerializer


class MemoryCinematicFragmentViewSet(viewsets.ModelViewSet):
    queryset = MemoryCinematicFragment.objects.all().order_by("-created_at")
    serializer_class = MemoryCinematicFragmentSerializer
