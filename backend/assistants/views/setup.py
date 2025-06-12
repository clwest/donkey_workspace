from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from assistants.serializers import AssistantSetupSummarySerializer


class AssistantSetupSummaryView(APIView):
    """Return initial setup summary info for an assistant."""

    def get(self, request, slug):
        assistant = get_object_or_404(Assistant, slug=slug)
        serializer = AssistantSetupSummarySerializer(assistant)
        return Response(serializer.data)
