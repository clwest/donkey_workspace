from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant


class InsightPlanView(APIView):
    def post(self, request, assistant_id):
        context_filter = request.data.get("context", "")
        assistant = get_object_or_404(Assistant, pk=assistant_id)
        plan_steps = assistant.generate_insight_plan(context_filter)
        return Response({"plan": plan_steps})
