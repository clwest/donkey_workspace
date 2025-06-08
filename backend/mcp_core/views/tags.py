from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count

from assistants.models.reflection import AssistantReflectionLog
from mcp_core.models import Tag

# mcp_core/views.py


@api_view(["GET"])
@permission_classes([AllowAny])
def top_tags(request):
    """Return the most common tags across all reflections."""
    tag_qs = (
        Tag.objects.annotate(count=Count("assistantreflectionlog"))
        .filter(count__gt=0)
        .order_by("-count")[:10]
    )

    return Response(
        [{"tag": tag.name, "slug": tag.slug, "count": tag.count} for tag in tag_qs]
    )
