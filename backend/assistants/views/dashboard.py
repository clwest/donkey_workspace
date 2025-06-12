from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from assistants.models.assistant import Assistant, DelegationEvent
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.project import AssistantNextAction
from intel_core.models import Document
from assistants.serializers import (
    AssistantSerializer,
    AssistantThoughtLogSerializer,
    DelegationEventSerializer,
    ProjectOverviewSerializer,
    AssistantNextActionSummarySerializer,
    DocumentChunkInfoSerializer,
    AssistantReflectionLogSerializer,
)
from project.models import ProjectTask
from project.serializers import ProjectTaskSerializer
from assistants.models.reflection import AssistantReflectionLog
from memory.services import MemoryService
from memory.serializers import MemoryEntrySlimSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_dashboard(request, slug):
    """Return dashboard context for the specified assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    project = assistant.current_project
    project_data = ProjectOverviewSerializer(project).data if project else None

    # Tasks and next actions
    tasks_data = []
    actions_data = []
    if project:
        linked_project = project.linked_projects.first()
        if linked_project:
            tasks = ProjectTask.objects.filter(project=linked_project).order_by(
                "priority"
            )[:5]
            tasks_data = ProjectTaskSerializer(tasks, many=True).data
        actions = AssistantNextAction.objects.filter(
            objective__project=project
        ).order_by("-created_at")[:5]
        actions_data = AssistantNextActionSummarySerializer(actions, many=True).data

    reflections = (
        AssistantReflectionLog.objects.filter(assistant=assistant)
        .filter(Q(tags__name="symbolic_change") | Q(tags__name="planning"))
        .distinct()
        .order_by("-created_at")[:5]
    )

    documents = []
    for doc in assistant.documents.all():
        total = doc.chunks.count()
        embedded = doc.chunks.filter(embedding__isnull=False).count()
        percent = round((embedded / total) * 100, 2) if total else 0.0
        documents.append(
            {
                "id": doc.id,
                "title": doc.title,
                "source_type": doc.source_type,
                "embedded_percent": percent,
                "embedded_chunks": embedded,
                "total_chunks": total,
            }
        )

    # use select_related/prefetch to avoid N+1 queries
    thoughts = (
        AssistantThoughtLog.objects.filter(assistant=assistant)
        .select_related("project")
        .prefetch_related("tags")
        .order_by("-created_at")[:5]
    )
    memories = MemoryService.filter_entries(assistant=assistant).order_by(
        "-created_at"
    )[:5]
    delegations = (
        DelegationEvent.objects.select_related("parent_assistant", "child_assistant")
        .filter(Q(parent_assistant=assistant) | Q(child_assistant=assistant))
        .order_by("-created_at")[:5]
    )

    data = {
        "assistant": AssistantSerializer(assistant).data,
        "project": project_data,
        "tasks": tasks_data,
        "next_actions": actions_data,
        "thoughts": AssistantThoughtLogSerializer(thoughts, many=True).data,
        "recent_memories": MemoryEntrySlimSerializer(memories, many=True).data,
        "delegations": DelegationEventSerializer(delegations, many=True).data,
        "reflections": AssistantReflectionLogSerializer(reflections, many=True).data,
        "documents": DocumentChunkInfoSerializer(documents, many=True).data,
    }
    return Response(data)
