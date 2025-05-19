from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from assistants.models import AssistantProject
from assistants.serializers import (
    AssistantProjectSerializer,
    AssistantFromPromptSerializer,
    AssistantSerializer,
)
from django.utils.text import slugify
from assistants.models import Assistant, AssistantProject
from prompts.models import Prompt
from prompts.utils.embeddings import get_prompt_embedding
from embeddings.helpers.helpers_io import save_embedding
import uuid

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistant_projects(request):
    if request.method == "GET":
        projects = AssistantProject.objects.all().order_by("-created_at")
        serializer = AssistantProjectSerializer(projects, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = AssistantProjectSerializer(data=request.data)

        if serializer.is_valid():
            project = serializer.save()
            return Response(AssistantProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        else:
            print("🚨 Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_project_detail(request, pk):
    try:
        project = AssistantProject.objects.get(pk=pk)
    except AssistantProject.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    if request.method == "GET":
        serializer = AssistantProjectSerializer(project)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def bootstrap_assistant_from_prompt(request):
    serializer = AssistantFromPromptSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    result = serializer.save()

    assistant_data = AssistantSerializer(result["assistant"]).data
    project_data = AssistantProjectSerializer(result["project"]).data

    return Response({
        "assistant": assistant_data,
        "project": project_data,
    }, status=201)

@api_view(["GET"])
def projects_for_assistant(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    projects = AssistantProject.objects.filter(assistant=assistant)
    serializer = AssistantProjectSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def assign_project(request, slug):
    """Assign an assistant's active project."""
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    project_id = request.data.get("project_id")
    if not project_id:
        return Response({"error": "project_id required"}, status=400)

    try:
        project = AssistantProject.objects.get(id=project_id)
    except AssistantProject.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    if project.assistant != assistant:
        return Response({"error": "Project does not belong to this assistant"}, status=400)

    assistant.current_project = project
    assistant.save()
    return Response({"status": "assigned"})
