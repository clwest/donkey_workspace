from rest_framework.views import APIView
from rest_framework.response import Response


class AdaptiveLoopTriggerView(APIView):
    def post(self, request, assistant_id):
        return Response({"status": "adjustments_applied"})
