from rest_framework import viewsets
from ..models import CinemythStoryline
from ..serializers import CinemythStorylineSerializer


class CinemythStorylineViewSet(viewsets.ModelViewSet):
    queryset = CinemythStoryline.objects.all().order_by("-created_at")
    serializer_class = CinemythStorylineSerializer
