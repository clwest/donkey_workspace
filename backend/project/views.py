"""Viewsets providing API endpoints for working with ``Project`` objects."""

from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from assistants.models import Assistant, AssistantReflectionLog
from memory.serializers import MemoryEntrySerializer
from assistants.serializers import AssistantReflectionLogSerializer
from assistants.helpers.team_memory import (
    assign_project_role,
    get_visible_memories,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD operations for :class:`Project` instances returned as JSON."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["POST"])
@permission_classes([AllowAny])
def assign_role(request, id):
    project = get_object_or_404(Project, id=id)
    assistant_id = request.data.get("assistant_id")
    role = request.data.get("role")
    if not assistant_id or not role:
        return Response({"error": "assistant_id and role required"}, status=400)
    assistant = get_object_or_404(Assistant, id=assistant_id)
    assign_project_role(assistant, project, role)
    return Response({"status": "assigned"})


@api_view(["GET"])
@permission_classes([AllowAny])
def team_memory(request, id):
    project = get_object_or_404(Project, id=id)
    assistant_id = request.GET.get("assistant_id")
    assistant = None
    if assistant_id:
        assistant = get_object_or_404(Assistant, id=assistant_id)
    mems = get_visible_memories(project, assistant)
    data = MemoryEntrySerializer(mems, many=True).data
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def team_reflections(request, id):
    project = get_object_or_404(Project, id=id)
    logs = AssistantReflectionLog.objects.filter(
        project__linked_projects=project
    ).order_by("-created_at")
    data = AssistantReflectionLogSerializer(logs, many=True).data
    return Response(data)
