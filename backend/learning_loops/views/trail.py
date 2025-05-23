from rest_framework import generics
from ..models import LearningTrailNode
from ..serializers import LearningTrailNodeSerializer


class LearningTrailNodeListCreateView(generics.ListCreateAPIView):
    queryset = LearningTrailNode.objects.all().order_by("-created_at")
    serializer_class = LearningTrailNodeSerializer
