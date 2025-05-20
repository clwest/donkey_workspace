# mcp_core/views/reflection.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from assistants.models import AssistantReflectionLog, Assistant
from assistants.serializers import AssistantReflectionLogSerializer
from project.models import Project
from mcp_core.serializers import ReflectionLogSerializer
from agents.utils.agent_reflection_engine import AgentReflectionEngine
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from mcp_core.models import MemoryContext, DevDoc, Tag
from embeddings.helpers.helpers_io import save_embedding
import json

from django.utils.timezone import now, timedelta
from collections import defaultdict


@api_view(["POST"])
@permission_classes([AllowAny])
def reflect_on_memories(request):
    target_type = request.data.get("target_type")
    since = request.data.get("since")
    limit = int(request.data.get("limit", 10))
    agent = AgentReflectionEngine(user=request.user)
    memories = agent.reflect_on(target_type=target_type, since=since, limit=limit)
    if not memories:
        return Response({"error": "No important memories found."}, status=400)
    reflection_out = agent.get_structured_reflection(memories)
    llm_summary = agent.get_llm_summary(memories)
    mood = agent.analyze_mood(llm_summary)
    reflection_data = json.loads(reflection_out)
    reflection = AssistantReflectionLog.objects.create(
        title=reflection_data.get("title", "Untitled Reflection"),
        summary=reflection_data.get("summary", ""),
        llm_summary=llm_summary,
        raw_prompt=agent.summarize_reflection(memories),
        mood=mood,
    )
    if hasattr(reflection, "related_memories"):
        reflection.related_memories.set(memories)
    tag_names = reflection_data.get("tags", [])
    if tag_names:
        tags = Tag.objects.filter(name__in=tag_names)
        reflection.tags.set(tags)
    save_embedding(reflection, embedding=[])
    return Response(ReflectionLogSerializer(reflection).data, status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def reflect_on_custom_memories(request):
    memory_ids = request.data.get("memory_ids", [])
    if not memory_ids:
        return Response({"error": "No memories provided."}, status=400)
    memories = MemoryContext.objects.filter(id__in=memory_ids)
    agent = AgentReflectionEngine(user=request.user)
    raw_summary = agent.summarize_reflection(memories)
    llm_summary = agent.expand_summary(raw_summary, memories=memories)
    reflection = AssistantReflectionLog.objects.create(
        title=agent.generate_reflection_title(raw_summary),
        raw_prompt=raw_summary,
        summary=llm_summary,
        llm_summary=llm_summary,
    )
    if hasattr(reflection, "related_memories"):
        reflection.related_memories.set(memories)
    save_embedding(reflection, embedding=[])
    return Response(ReflectionLogSerializer(reflection).data, status=200)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_reflections(request):
    reflections = AssistantReflectionLog.objects.order_by("-created_at")
    return Response(ReflectionLogSerializer(reflections, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def reflection_detail(request, reflection_id):
    try:
        reflection = AssistantReflectionLog.objects.get(id=reflection_id)
    except AssistantReflectionLog.DoesNotExist:
        return Response({"error": "Reflection not found."}, status=404)
    return Response(ReflectionLogSerializer(reflection).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def expand_reflection(request, pk):
    try:
        reflection = AssistantReflectionLog.objects.get(id=pk)
    except AssistantReflectionLog.DoesNotExist:
        return Response({"error": "Reflection not found"}, status=404)
    agent = AgentReflectionEngine(user=request.user)
    expanded_summary = agent.expand_summary(
        reflection.summary, reflection.related_memories.all()
    )
    reflection.summary = expanded_summary
    reflection.save()
    return Response(
        {"reflection_id": reflection.id, "updated_summary": expanded_summary}
    )


@api_view(["GET"])
def project_reflections(request, project_id):
    reflections = AssistantReflectionLog.objects.filter(project_id=project_id).order_by(
        "-created_at"
    )
    serializer = AssistantReflectionLogSerializer(reflections, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def reflect_on_agent_project(request, assistant_id):
    try:
        project = Project.objects.get(id=assistant_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=404)

    reflection = project.reflect()

    if reflection:
        return Response(
            {
                "reflection_id": reflection.id,
                "title": reflection.title,
                "mood": reflection.mood,
                "summary": reflection.summary,
                "llm_summary": reflection.llm_summary,
                "created_at": reflection.created_at,
            }
        )
    else:
        return Response({"message": "No memories to reflect on."}, status=400)


@api_view(["GET"])
@permission_classes([AllowAny])
def recent_reflections(request):
    """
    GET endpoint to return the 5 most recent reflections.
    Useful for dashboard previews, homepages, etc.
    """
    reflections = AssistantReflectionLog.objects.order_by("-created_at")[:5]

    data = [
        {
            "id": r.id,
            "title": r.title,
            "tags": r.tags,
            "summary": r.summary[:200] + "..." if r.summary else "",
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for r in reflections
    ]

    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def reflections_by_tag(request, tag_name):
    """
    GET reflections that contain a specific tag.
    """
    reflections = AssistantReflectionLog.objects.filter(
        tags__contains=[tag_name]
    ).order_by("-created_at")
    serializer = ReflectionLogSerializer(reflections, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def save_reflection(request, reflection_id):
    try:
        reflection = AssistantReflectionLog.objects.get(id=reflection_id)
        reflection.important = True
        reflection.save()
        return Response({"message": "Reflection saved!"})
    except AssistantReflectionLog.DoesNotExist:
        return Response({"error": "Reflection not found"}, status=404)



@api_view(["GET"])
@permission_classes([AllowAny])
def grouped_reflections_view(request):
    # Optional query params: assistant_id, project_id, tag
    assistant_id = request.GET.get("assistant")
    project_id = request.GET.get("project")
    tag = request.GET.get("tag")

    reflections = AssistantReflectionLog.objects.all()

    if assistant_id:
        reflections = reflections.filter(assistant_id=assistant_id)
    if project_id:
        reflections = reflections.filter(project_id=project_id)
    if tag:
        reflections = reflections.filter(tags__name__icontains=tag)

    grouped = defaultdict(list)

    for reflection in reflections:
        delta = now() - reflection.created_at
        if delta.days == 0:
            group_key = "🟢 Today"
        elif delta.days < 7:
            group_key = "🟡 This Week"
        elif delta.days < 30:
            group_key = "🟠 This Month"
        else:
            group_key = "🔵 Older"

        grouped[group_key].append(reflection)

    response_data = []
    for group_title, items in grouped.items():
        serialized_items = AssistantReflectionLogSerializer(items, many=True).data
        response_data.append({
            "group": group_title,
            "count": len(items),
            "reflections": serialized_items,
        })

    return Response({"groups": response_data})
