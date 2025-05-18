from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from assistants.models import (
    AssistantMemoryChain,
    AssistantReflectionInsight,
    Assistant,
    AssistantReflectionLog,
)
from assistants.serializers import (
    AssistantMemoryChainSerializer,
    AssistantReflectionInsightSerializer,
    AssistantReflectionLogSerializer,
)
from project.models import ProjectMemoryLink
from project.serializers import ProjectMemoryLinkSerializer

from memory.models import MemoryEntry
from memory.serializers import MemoryEntrySerializer


# Assistant Memory Chains
@api_view(["GET", "POST"])
def assistant_memory_chains(request, project_id):
    if request.method == "GET":
        chains = AssistantMemoryChain.objects.filter(project_id=project_id)
        serializer = AssistantMemoryChainSerializer(chains, many=True)
        return Response(serializer.data)
    if request.method == "POST":
        serializer = AssistantMemoryChainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_id=project_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def linked_memories(request, project_id):
    links = ProjectMemoryLink.objects.filter(project_id=project_id)
    serializer = ProjectMemoryLinkSerializer(links, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def link_memory_to_project(request):
    serializer = ProjectMemoryLinkSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Assistant Reflection Insights
@api_view(["GET"])
def assistant_project_reflections(request, project_id):
    reflections = AssistantReflectionLog.objects.filter(project_id=project_id).order_by(
        "-created_at"
    )
    serializer = AssistantReflectionLogSerializer(reflections, many=True)
    return Response(serializer.data)


