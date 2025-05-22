from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import SimulationConfig, SimulationRunLog


class SimulationRunView(APIView):
    def post(self, request):
        config_id = request.data.get("config_id")
        config = get_object_or_404(SimulationConfig, pk=config_id)
        run = SimulationRunLog.objects.create(config=config, status="pending")
        return Response({"run_id": run.id})
