from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assistants.models import Assistant


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_demo_recap(request, pk):
    """Return a placeholder recap for a demo assistant."""
    assistant = get_object_or_404(Assistant, pk=pk)
    return Response(
        {
            "slug": assistant.slug,
            "demo_summary": "This is a placeholder recap for demo assistant.",
        }
    )
