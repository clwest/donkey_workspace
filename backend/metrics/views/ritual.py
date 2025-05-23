from rest_framework import generics
from ..models import RitualPerformanceMetric
from ..serializers import RitualPerformanceMetricSerializer


class RitualPerformanceMetricListCreateView(generics.ListCreateAPIView):
    queryset = RitualPerformanceMetric.objects.all().order_by("-created_at")
    serializer_class = RitualPerformanceMetricSerializer
