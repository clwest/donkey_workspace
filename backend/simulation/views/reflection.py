from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import MythflowReflectionLoop, MythflowSession
from ..serializers import MythflowReflectionLoopSerializer
from ..utils import calculate_narrative_pressure


class MythflowReflectionLoopViewSet(viewsets.ModelViewSet):
    queryset = MythflowReflectionLoop.objects.all().order_by("-created_at")
    serializer_class = MythflowReflectionLoopSerializer


class NarrativePressureView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response({"detail": "session_id required"}, status=400)
        data = calculate_narrative_pressure(int(session_id))
        return Response(data)
