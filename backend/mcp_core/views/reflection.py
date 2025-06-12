# mcp_core/views/reflection.py
from rest_framework.decorators import api_view, permission_classes, action, throttle_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
import warnings
from rest_framework.throttling import UserRateThrottle
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.assistant import Assistant
from assistants.serializers_pass import AssistantReflectionLogSerializer
from project.models import Project
from mcp_core.serializers import ReflectionLogSerializer
from agents.utils.agent_reflection_engine import AgentReflectionEngine
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from mcp_core.models import MemoryContext, DevDoc, Tag
from mcp_core.serializers_tags import TagSerializer
from embeddings.helpers.helpers_io import save_embedding
import json

from django.utils.timezone import now, timedelta
from collections import defaultdict


class ReflectionViewSet(viewsets.ModelViewSet):
    queryset = AssistantReflectionLog.objects.all().order_by("-created_at")
    serializer_class = ReflectionLogSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])  # /reflections/reflect/
    def reflect(self, request):
        warnings.warn(
            "Deprecated function endpoints; use this action instead",
            DeprecationWarning,
        )
        # `reflect_on_memories` is a function-based view decorated with
        # `@api_view`, which expects a `django.http.HttpRequest`. When called
        # directly from a DRF viewset action we receive a DRF `Request` object,
        # which triggers an assertion inside the decorator. Passing the
        # underlying HttpRequest avoids that issue.
        return reflect_on_memories(request._request)

    @action(detail=True, methods=["post"])  # /reflections/<pk>/expand/
    def expand(self, request, pk=None):
        return expand_reflection(request._request, pk)

    @action(detail=False, methods=["get"], url_path="recent")
    def recent(self, request):
        return recent_reflections(request._request)

    @action(detail=False, methods=["get"], url_path="grouped")
    def grouped(self, request):
        return grouped_reflections_view(request._request)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([UserRateThrottle])
def reflect_on_memories(request):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/reflections/reflect/",
        DeprecationWarning,
    )
    target_type = request.data.get("target_type")
    since = request.data.get("since")
    limit = int(request.data.get("limit", 10))
    from mcp_core.tasks.async_tasks import reflect_on_memories_task

    task = reflect_on_memories_task.delay(request.user.id if request.user else None, target_type, since, limit)
    return Response({"task_id": task.id}, status=202)



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

class ReflectionListView(generics.ListAPIView):
    queryset = AssistantReflectionLog.objects.order_by("-created_at")
    serializer_class = ReflectionLogSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination


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
    warnings.warn(
        "Deprecated: use /api/v1/mcp/reflections/<id>/expand/",
        DeprecationWarning,
    )
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

    data = []
    for r in reflections:
        serialized_tags = TagSerializer(r.tags.all(), many=True).data
        data.append(
            {
                "id": r.id,
                "title": r.title,
                "tags": serialized_tags,
                "summary": r.summary[:200] + "..." if r.summary else "",
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        )

    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def reflections_by_tag(request, tag_name):
    """
    GET reflections that contain a specific tag.
    """
    if not tag_name or tag_name == "undefined":
        return Response({"error": "Tag name required"}, status=400)

    reflections = AssistantReflectionLog.objects.filter(
        tags__slug__iexact=tag_name
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
        response_data.append(
            {
                "group": group_title,
                "count": len(items),
                "reflections": serialized_items,
            }
        )

    return Response({"groups": response_data})


@api_view(["GET"])
@permission_classes([AllowAny])
def task_status(request, task_id):
    from celery.result import AsyncResult

    res = AsyncResult(task_id)
    data = {"task_id": task_id, "status": res.status}
    if res.status == "SUCCESS":
        data["result"] = res.result
    return Response(data)
