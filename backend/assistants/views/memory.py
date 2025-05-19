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
    AssistantReflectionLogListSerializer,
    AssistantReflectionLogDetailSerializer,
)
from project.models import ProjectMemoryLink
from project.serializers import ProjectMemoryLinkSerializer

from memory.models import MemoryEntry
from memory.serializers import MemoryEntrySerializer, MemoryEntrySlimSerializer
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from memory.utils.context_helpers import get_or_create_context_from_memory
from mcp_core.models import MemoryContext
from django.contrib.contenttypes.models import ContentType
from intel_core.models import Document
from project.models import Project


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


@api_view(["GET"])
def assistant_memories(request, slug):
    """List memory entries for a specific assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    entries = MemoryEntry.objects.filter(assistant=assistant).order_by("-created_at")
    serializer = MemoryEntrySlimSerializer(entries, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def reflect_now(request, slug):
    """Trigger an immediate reflection using optional context."""
    assistant = get_object_or_404(Assistant, slug=slug)

    memory_id = request.data.get("memory_id")
    project_id = request.data.get("project_id")
    doc_id = request.data.get("doc_id")

    context = None
    if memory_id:
        memory = get_object_or_404(MemoryEntry, id=memory_id)
        context = get_or_create_context_from_memory(memory)
    elif project_id:
        project = get_object_or_404(Project, id=project_id)
        context = MemoryContext.objects.create(
            target_content_type=ContentType.objects.get_for_model(Project),
            target_object_id=project.id,
            content=project.title,
        )
    elif doc_id:
        document = get_object_or_404(Document, id=doc_id)
        context = MemoryContext.objects.create(
            target_content_type=ContentType.objects.get_for_model(Document),
            target_object_id=document.id,
            content=document.title,
        )
    else:
        context = MemoryContext.objects.create(content="ad-hoc reflection")

    engine = AssistantReflectionEngine(assistant)
    summary = engine.reflect_now(context)
    return Response({"summary": summary})


@api_view(["GET"])
def assistant_reflection_logs(request, slug):
    """List all reflection logs for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    reflections = (
        AssistantReflectionLog.objects.filter(assistant=assistant)
        .order_by("-created_at")
    )
    serializer = AssistantReflectionLogListSerializer(reflections, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def assistant_reflection_detail(request, id):
    """Retrieve full reflection log details."""
    reflection = get_object_or_404(AssistantReflectionLog, id=id)
    serializer = AssistantReflectionLogDetailSerializer(reflection)
    return Response(serializer.data)


