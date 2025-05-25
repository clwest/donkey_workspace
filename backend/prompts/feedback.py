from rest_framework.views import APIView
from rest_framework.response import Response

from metrics.models import PromptVersionTrace


class PromptFeedbackRefinementView(APIView):
    """Return prompt version traces with feedback."""

    def get(self, request, prompt_id):
        traces = PromptVersionTrace.objects.filter(prompt_id=prompt_id).order_by("-created_at")
        return Response({"traces": list(traces.values())})
