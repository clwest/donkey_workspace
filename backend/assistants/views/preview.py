from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from assistants.serializers import AssistantPreviewSerializer


@api_view(["GET"])
def assistant_preview(request, slug):
    """Return a minimal preview for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    serializer = AssistantPreviewSerializer(assistant)
    return Response(serializer.data)
