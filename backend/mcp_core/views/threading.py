# mcp_core/views/threading.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import models
from mcp_core.models import (
    MemoryContext,
    NarrativeThread,
    Tag,
)
from mcp_core.serializers_tags import (
    NarrativeThreadSerializer,
)
from mcp_core.utils.thread_diagnostics import run_thread_diagnostics


from mcp_core.serializers_tags import (
    NarrativeThreadSerializer,
    ThreadObjectiveReflectionSerializer,
)
from mcp_core.utils.thread_helpers import (
    get_or_create_thread,
    attach_memory_to_thread,
    generate_thread_reflection,
    generate_thread_refocus_prompt,
    suggest_continuity,
)
from assistants.models import AssistantThoughtLog
from django.utils import timezone


@api_view(["POST"])
def thread_from_memory(request):
    """
    Create a narrative thread from a single memory.
    Expects: { "memory_id": "<uuid>", "title": "optional" }
    """
    memory_id = request.data.get("memory_id")
    title = request.data.get("title")

    memory = get_object_or_404(MemoryContext, id=memory_id)

    if not title:
        title = memory.category or memory.content[:40] + "..."

    thread = get_or_create_thread(title=title)
    attach_memory_to_thread(memory, thread)

    return Response(NarrativeThreadSerializer(thread).data)


@api_view(["POST"])
def auto_thread_by_tag(request):
    """
    Automatically group all memories that share a tag into a thread.
    Expects: { "tag_slug": "<slug>", "title": "optional" }
    """
    slug = request.data.get("tag_slug")
    title = request.data.get("title")

    tag = get_object_or_404(Tag, slug=slug)
    memories = tag.memory_contexts.all()

    if not memories.exists():
        return Response({"detail": "No memories found for tag."}, status=400)

    thread_title = title or f"Tag: {tag.name}"
    thread = get_or_create_thread(thread_title)
    for memory in memories:
        attach_memory_to_thread(memory, thread)

    return Response(NarrativeThreadSerializer(thread).data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def narrative_thread_list(request):
    if request.method == "GET":
        threads = NarrativeThread.objects.all().order_by("-created_at")
        serializer = NarrativeThreadSerializer(threads, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = NarrativeThreadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_overview_threads(request):
    """Return threads with activity metrics for dashboard overview."""
    threads = NarrativeThread.objects.all()

    assistant = request.GET.get("assistant")
    project = request.GET.get("project")
    if assistant:
        threads = threads.filter(memories__assistant_id=assistant).distinct()
    if project:
        threads = threads.filter(memories__related_project_id=project).distinct()

    serialized = [NarrativeThreadSerializer(t).data for t in threads]
    serialized.sort(
        key=lambda x: x.get("last_updated") or "",
        reverse=True,
    )
    return Response(serialized)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def narrative_thread_detail(request, id):
    thread = get_object_or_404(NarrativeThread, id=id)

    if request.method == "GET":
        serializer = NarrativeThreadSerializer(thread)
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = NarrativeThreadSerializer(thread, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    elif request.method == "DELETE":
        thread.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(
        {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def diagnose_thread(request, thread_id):
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    result = run_thread_diagnostics(thread)
    return Response(result)


@api_view(["POST"])
@permission_classes([AllowAny])
def suggest_continuity_view(request, thread_id):
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    result = suggest_continuity(thread_id)
    thread._link_suggestions = result.get("link_suggestions", [])
    serializer = NarrativeThreadSerializer(thread)
    data = serializer.data
    data.update(result)
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_thread_diagnostics(request, thread_id):
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    logs = ThreadDiagnosticLog.objects.filter(thread=thread).order_by("-created_at")
    return Response(ThreadDiagnosticLogSerializer(logs, many=True).data)


# <<<<<<< codex/add-healing-suggestions-for-low-continuity-threads

# @api_view(["POST"])
# @permission_classes([AllowAny])
# def reflect_on_thread_objective(request, thread_id):
#     thread = get_object_or_404(NarrativeThread, id=thread_id)
#     reflection_text = generate_thread_reflection(thread)
#     reflection = ThreadObjectiveReflection.objects.create(
#         thread=thread,
#         thought=reflection_text,
#         created_by=None,
#     )
#     serializer = ThreadObjectiveReflectionSerializer(reflection)
#     return Response(serializer.data, status=201)


# @api_view(["GET"])
# @permission_classes([AllowAny])
# def diagnose_thread(request, thread_id):
#     """Return a simple continuity score for the thread."""
#     thread = get_object_or_404(NarrativeThread, id=thread_id)
#     memory_count = thread.related_memories.count()
#     memory_count += MemoryContext.objects.filter(
#         models.Q(narrative_thread=thread) | models.Q(thread=thread)
#     ).count()
#     if thread.origin_memory:
#         memory_count += 1
#     score = min(1.0, memory_count / 5)
#     refocus_prompt = None
#     if score < 0.5:
#         refocus_prompt = generate_thread_refocus_prompt(thread)
#         AssistantThoughtLog.objects.create(
#             thought_type="refocus",
#             thought=refocus_prompt,
#             narrative_thread=thread,
#         )
#         thread.last_refocus_prompt = timezone.now()
#         thread.save(update_fields=["last_refocus_prompt"])
#     return Response(
#         {"continuity_score": round(score, 2), "refocus_prompt": refocus_prompt}
#     )


# @api_view(["POST"])
# @permission_classes([AllowAny])
# def refocus_thread(request, thread_id):
#     thread = get_object_or_404(NarrativeThread, id=thread_id)
#     prompt = generate_thread_refocus_prompt(thread)
#     AssistantThoughtLog.objects.create(
#         thought_type="refocus",
#         thought=prompt,
#         narrative_thread=thread,
#     )
#     thread.last_refocus_prompt = timezone.now()
#     thread.save(update_fields=["last_refocus_prompt"])
#     return Response({"prompt": prompt})
# =======
# >>>>>>> main
