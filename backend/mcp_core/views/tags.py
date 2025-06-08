from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count

from mcp_core.models import Tag

# mcp_core/views.py


@api_view(["GET"])
@permission_classes([AllowAny])
def top_tags(request):
    """
    Return the most common tags across all reflections.
    """
    tags = Tag.objects.annotate(count=Count("assistantreflectionlog")).order_by(
        "-count"
    )[:10]

    return Response([{"tag": t.name, "count": t.count} for t in tags])
