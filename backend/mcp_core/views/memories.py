from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from rest_framework.throttling import UserRateThrottle

from mcp_core.models import MemoryContext, NarrativeThread, ThreadSplitLog
from mcp_core.serializers import MemoryContextSerializer
from django.shortcuts import get_object_or_404
from memory.models import MemoryEntry
from assistants.models import AssistantThoughtLog, AssistantReflectionLog

from mcp_core.serializers import MemoryContextSerializer

class MemoryListView(generics.ListAPIView):
    queryset = MemoryContext.objects.order_by("-created_at")
    serializer_class = MemoryContextSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination


@api_view(["PATCH"])
@permission_classes([AllowAny])
def relink_memory(request, id):
    """Move a memory entry and its related logs to a different thread."""

    memory = get_object_or_404(MemoryEntry, id=id)
    thread_id = request.data.get("new_thread_id")
    if not thread_id:
        return Response({"error": "new_thread_id required"}, status=400)
    new_thread = get_object_or_404(NarrativeThread, id=thread_id)

    old_thread = memory.thread
    memory.thread = new_thread
    memory.save(update_fields=["thread"])

    AssistantThoughtLog.objects.filter(linked_memory=memory).update(
        narrative_thread=new_thread
    )
    if hasattr(AssistantReflectionLog, "thread"):
        AssistantReflectionLog.objects.filter(linked_memory=memory).update(
            thread=new_thread
        )

    ThreadSplitLog.objects.create(
        from_thread=old_thread, to_thread=new_thread, moved_entry=memory
    )

    return Response({"status": "ok"})
