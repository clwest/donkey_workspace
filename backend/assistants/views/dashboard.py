from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from assistants.models import Assistant, AssistantThoughtLog, DelegationEvent
from assistants.serializers import (
    AssistantSerializer,
    AssistantThoughtLogSerializer,
    DelegationEventSerializer,
    ProjectOverviewSerializer,
)
from memory.models import MemoryEntry
from memory.serializers import MemoryEntrySlimSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_dashboard(request, slug):
    """Return dashboard context for the specified assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    project = assistant.current_project
    project_data = ProjectOverviewSerializer(project).data if project else None

    # use select_related/prefetch to avoid N+1 queries
    thoughts = (
        AssistantThoughtLog.objects.filter(assistant=assistant)
        .select_related("project")
        .prefetch_related("tags")
        .order_by("-created_at")[:5]
    )
    memories = (
        MemoryEntry.objects.filter(assistant=assistant)
        .select_related("document")
        .order_by("-created_at")[:5]
    )
    delegations = (
        DelegationEvent.objects.select_related("parent_assistant", "child_assistant")
        .filter(Q(parent_assistant=assistant) | Q(child_assistant=assistant))
        .order_by("-created_at")[:5]
    )

    data = {
        "assistant": AssistantSerializer(assistant).data,
        "project": project_data,
        "thoughts": AssistantThoughtLogSerializer(thoughts, many=True).data,
        "recent_memories": MemoryEntrySlimSerializer(memories, many=True).data,
        "delegations": DelegationEventSerializer(delegations, many=True).data,
    }
    return Response(data)
