"""Viewsets providing API endpoints for working with ``Project`` objects."""

from rest_framework import viewsets
from django.db.models import Q
from .models import Project, ProjectTask, ProjectMilestone
from .serializers import (
    ProjectSerializer,
    ProjectTaskSerializer,
    ProjectMilestoneSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from memory.serializers import MemoryEntrySerializer
from assistants.serializers import AssistantReflectionLogSerializer
from .services import projects as project_services

class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD operations for :class:`Project` instances returned as JSON."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return projects owned by the user, where the user is a participant,
        or that are marked as public."""
        user = self.request.user
        return (
            Project.objects.filter(
                Q(user=user)
                | Q(participants=user)
                | Q(is_public=True)
            )
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(detail=True, methods=["post"], url_path="assign_role")
    def assign_role(self, request, pk=None):
        project = get_object_or_404(Project, id=pk)
        if not project_services.user_can_access_project(request.user, project):
            return Response(status=status.HTTP_403_FORBIDDEN)
        assistant_id = request.data.get("assistant_id")
        role = request.data.get("role")
        if not assistant_id or not role:
            return Response({"error": "assistant_id and role required"}, status=400)
        project_services.assign_role_to_assistant(project, assistant_id, role)
        return Response({"status": "assigned"})


    @action(detail=True, methods=["get"], url_path="team_memory")
    def team_memory(self, request, pk=None):
        project = get_object_or_404(Project, id=pk)
        if not project_services.user_can_access_project(request.user, project):
            return Response(status=status.HTTP_403_FORBIDDEN)
        assistant_id = request.GET.get("assistant_id")
        mems = project_services.fetch_team_memories(project, assistant_id)
        data = MemoryEntrySerializer(mems, many=True).data
        return Response(data)


    @action(detail=True, methods=["get"], url_path="team_reflections")
    def team_reflections(self, request, pk=None):
        project = get_object_or_404(Project, id=pk)
        if not project_services.user_can_access_project(request.user, project):
            return Response(status=status.HTTP_403_FORBIDDEN)
        logs = project_services.fetch_team_reflections(project)
        data = AssistantReflectionLogSerializer(logs, many=True).data
        return Response(data)


class ProjectTaskViewSet(viewsets.ModelViewSet):
    """Manage tasks for a specific project (``project_pk`` URL kwarg)."""

    serializer_class = ProjectTaskSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProjectTask.objects.filter(
            project_id=self.kwargs.get("project_pk"),
            project__user=self.request.user,
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs.get("project_pk"))


class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    """Manage milestones for a specific project (``project_pk`` URL kwarg)."""

    serializer_class = ProjectMilestoneSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProjectMilestone.objects.filter(
            project_id=self.kwargs.get("project_pk"),
            project__user=self.request.user,
        )

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs.get("project_pk"))
