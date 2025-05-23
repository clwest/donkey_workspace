from rest_framework import generics
from ..models import AdaptiveLoopConfig
# from ..serializers import AdaptiveLoopConfigSerializer


class AdaptiveLoopConfigListCreateView(generics.ListCreateAPIView):
    queryset = AdaptiveLoopConfig.objects.all().order_by("-created_at")
    # serializer_class = AdaptiveLoopConfigSerializer
