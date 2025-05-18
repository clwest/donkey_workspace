from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from assistants.models import AssistantReflectionLog

# mcp_core/views.py


@api_view(["GET"])
@permission_classes([AllowAny])
def top_tags(request):
    """
    Return the most common tags across all reflections.
    """
    tag_counter = {}

    all_tags = AssistantReflectionLog.objects.values_list("tags", flat=True)

    for tags_list in all_tags:
        if tags_list:
            for tag in tags_list:
                tag_counter[tag] = tag_counter.get(tag, 0) + 1

    sorted_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)[:10]

    return Response([{"tag": tag, "count": count} for tag, count in sorted_tags])
