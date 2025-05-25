from rest_framework.views import APIView
from rest_framework.response import Response

from metrics.models import TaskEvolutionSuggestion


class SwarmTaskEvolutionView(APIView):
    """Return recent task evolution suggestions."""

    def get(self, request):
        suggestions = TaskEvolutionSuggestion.objects.all().order_by("-created_at")[:50]
        return Response({"suggestions": list(suggestions.values())})
