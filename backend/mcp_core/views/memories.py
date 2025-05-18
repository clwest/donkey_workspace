from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from mcp_core.models import MemoryContext


@api_view(["GET"])
@permission_classes([AllowAny])
def list_memories(request):
    memories = MemoryContext.objects.order_by("-created_at")[
        :100
    ]  # limit to latest 100
    data = [
        {
            "id": memory.id,
            "content": memory.content,
            "created_at": memory.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for memory in memories
    ]
    return Response(data)
