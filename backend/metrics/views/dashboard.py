from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import PerformanceMetric


class PerformanceDashboardView(APIView):
    def get(self, request, assistant_id):
        metrics = PerformanceMetric.objects.filter(assistant_id=assistant_id)
        return Response({"metrics": list(metrics.values())})
