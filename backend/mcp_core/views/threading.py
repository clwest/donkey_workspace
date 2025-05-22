# mcp_core/views/threading.py

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
import warnings

from django.shortcuts import get_object_or_404
from django.db import models
from itertools import chain
from mcp_core.models import (
    MemoryContext,
    NarrativeThread,
    Tag,
    ThreadMergeLog,
    ThreadSplitLog,
    ThreadDiagnosticLog,
    ThreadObjectiveReflection,
)
from mcp_core.serializers_tags import (
    NarrativeThreadSerializer,
    ThreadObjectiveReflectionSerializer,
)

from mcp_core.serializers_threads import ThreadDiagnosticLogSerializer

from mcp_core.serializers_replay import ThreadReplayItemSerializer

from memory.serializers import NarrativeThreadOverviewSerializer
from mcp_core.utils.thread_diagnostics import run_thread_diagnostics
from memory.models import MemoryEntry
from assistants.models import AssistantThoughtLog, AssistantReflectionLog
from assistants.utils.planning_alignment import suggest_planning_realignment
from mcp_core.utils.thread_helpers import (
    get_or_create_thread,
    attach_memory_to_thread,
    generate_thread_reflection,
    generate_thread_refocus_prompt,
    suggest_continuity,
)
from memory.models import MemoryEntry
from django.utils import timezone


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = NarrativeThread.objects.all().order_by("-created_at")
    serializer_class = NarrativeThreadSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=["post"])
    def merge(self, request, pk=None):
        return merge_thread(request, id=pk)

    @action(detail=True, methods=["post"])
    def split(self, request, pk=None):
        return split_thread(request, id=pk)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        return thread_summary(request, id=pk)

    @action(detail=True, methods=["get"])
    def replay(self, request, pk=None):
        return thread_replay(request, thread_id=pk)

    @action(detail=True, methods=["post"])
    def diagnose(self, request, pk=None):
        return diagnose_thread(request, thread_id=pk)

    @action(detail=True, methods=["post"], url_path="suggest-continuity")
    def suggest_continuity(self, request, pk=None):
        return suggest_continuity_view(request, thread_id=pk)

    @action(detail=True, methods=["post"])
    def realign(self, request, pk=None):
        return realign_thread(request, thread_id=pk)

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        return thread_progress(request, id=pk)

    @action(detail=True, methods=["post"])  # /threads/<id>/refocus/
    def refocus(self, request, pk=None):
        return refocus_thread(request, thread_id=pk)

    @action(detail=True, methods=["post"])  # /threads/<id>/reflect/
    def reflect(self, request, pk=None):
        return reflect_on_thread_objective(request, thread_id=pk)

    @action(detail=True, methods=["post"], url_path="set_objective")
    def set_objective(self, request, pk=None):
        thread = self.get_object()
        thread.long_term_objective = request.data.get("objective", "")
        thread.save(update_fields=["long_term_objective"])
        return Response({"objective": thread.long_term_objective})

    @action(detail=True, methods=["get"], url_path="objective")
    def objective(self, request, pk=None):
        thread = self.get_object()
        return Response({"objective": thread.long_term_objective})

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


class NarrativeThreadListView(generics.ListCreateAPIView):
    queryset = NarrativeThread.objects.all().order_by("-created_at")
    serializer_class = NarrativeThreadSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination


class OverviewThreadListView(generics.ListAPIView):
    serializer_class = NarrativeThreadOverviewSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        threads = NarrativeThread.objects.all()
        assistant = self.request.GET.get("assistant")
        project = self.request.GET.get("project")
        if assistant:
            threads = threads.filter(memories__assistant_id=assistant).distinct()
        if project:
            threads = threads.filter(memories__related_project_id=project).distinct()
        return threads

    def list(self, request, *args, **kwargs):
        cache_key = "overview_threads"
        if request.query_params.get("page", "1") == "1":
            cached = cache.get(cache_key)
            if cached:
                return Response(cached)
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, 300)
            return response
        return super().list(request, *args, **kwargs)


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


@api_view(["GET"])
@permission_classes([AllowAny])
def thread_summary(request, id):
    """Return ordered summary of a thread's memories, thoughts, reflections."""
    cache_key = f"thread_summary_{id}"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    cache_key = f"thread_summary_{id}"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    thread = get_object_or_404(NarrativeThread, id=id)

    memories = MemoryEntry.objects.filter(thread=thread).order_by("created_at")
    thoughts = AssistantThoughtLog.objects.filter(narrative_thread=thread).order_by(
        "created_at"
    )
    reflections = AssistantReflectionLog.objects.filter(
        linked_memory__thread=thread
    ).order_by("created_at")

    data = {
        "id": str(thread.id),
        "title": thread.title,
        "memories": [
            {
                "id": str(m.id),
                "preview": m.event[:100],
                "created_at": m.created_at,
                "tags": m.context_tags,
                "token_count": len((m.event or "").split()),
            }
            for m in memories
        ],
        "thoughts": [
            {
                "id": str(t.id),
                "content": t.thought[:100],
                "created_at": t.created_at,
                "type": t.thought_type,
                "model": t.mode,
            }
            for t in thoughts
        ],
        "reflections": [
            {
                "id": str(r.id),
                "summary": r.summary[:100],
                "created_at": r.created_at,
            }
            for r in reflections
        ],
    }
    cache.set(cache_key, data, 300)
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def thread_replay(request, thread_id):
    """Return merged timeline of memories, thoughts, and reflections."""
    cache_key = f"thread_replay_{thread_id}_{request.GET.get('with_context','0')}"

    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    thread = get_object_or_404(NarrativeThread, id=thread_id)
    with_context = request.GET.get("with_context") == "true"

    memories = list(MemoryEntry.objects.filter(thread=thread))
    thoughts = list(AssistantThoughtLog.objects.filter(narrative_thread=thread))
    reflections = list(
        AssistantReflectionLog.objects.filter(linked_memory__thread=thread)
    )

    items = list(chain(memories, thoughts, reflections))
    items.sort(key=lambda x: x.created_at)

    serializer = ThreadReplayItemSerializer(
        items, many=True, context={"with_context": with_context}
    )
    cache.set(cache_key, serializer.data, 300)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def diagnose_thread(request, thread_id):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/threads/<id>/diagnose/",
        DeprecationWarning,
    )
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    result = run_thread_diagnostics(thread)
    return Response(result)


@api_view(["POST"])
@permission_classes([AllowAny])
def suggest_continuity_view(request, thread_id):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/threads/<id>/suggest-continuity/",
        DeprecationWarning,
    )
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    result = suggest_continuity(thread_id)
    thread._link_suggestions = result.get("link_suggestions", [])
    serializer = NarrativeThreadSerializer(thread)
    data = serializer.data
    data.update(result)
    return Response(data)



# @api_view(["GET"])
# @permission_classes([AllowAny])
# def list_thread_diagnostics(request, thread_id):
#     thread = get_object_or_404(NarrativeThread, id=thread_id)
#     logs = ThreadDiagnosticLog.objects.filter(thread=thread).order_by("-created_at")
#     return Response(ThreadDiagnosticLogSerializer(logs, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def reflect_on_thread_objective(request, thread_id):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/threads/<id>/reflect/",
        DeprecationWarning,
    )
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    reflection_text = generate_thread_reflection(thread)
    reflection = ThreadObjectiveReflection.objects.create(
        thread=thread,
        thought=reflection_text,
        created_by=None,
    )
    serializer = ThreadObjectiveReflectionSerializer(reflection)
    return Response(serializer.data, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def diagnose_thread(request, thread_id):
    """Return a simple continuity score for the thread."""
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    memory_count = thread.related_memories.count()
    memory_count += MemoryContext.objects.filter(
        models.Q(narrative_thread=thread) | models.Q(thread=thread)
    ).count()
    if thread.origin_memory:
        memory_count += 1
    score = min(1.0, memory_count / 5)
    refocus_prompt = None
    if score < 0.5:
        refocus_prompt = generate_thread_refocus_prompt(thread)
        AssistantThoughtLog.objects.create(
            thought_type="refocus",
            thought=refocus_prompt,
            narrative_thread=thread,
        )
        thread.last_refocus_prompt = timezone.now()
        thread.save(update_fields=["last_refocus_prompt"])
    return Response(
        {"continuity_score": round(score, 2), "refocus_prompt": refocus_prompt}
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def refocus_thread(request, thread_id):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/threads/<id>/refocus/",
        DeprecationWarning,
    )
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    prompt = generate_thread_refocus_prompt(thread)
    AssistantThoughtLog.objects.create(
        thought_type="refocus",
        thought=prompt,
        narrative_thread=thread,
    )
    thread.last_refocus_prompt = timezone.now()
    thread.save(update_fields=["last_refocus_prompt"])
    return Response({"prompt": prompt})


@api_view(["POST"])
@permission_classes([AllowAny])
def realign_thread(request, thread_id):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/threads/<id>/realign/",
        DeprecationWarning,
    )
    """Run planning realignment based on diagnostics and mood."""
    from mcp_core.tasks.async_tasks import realign_thread_task
    task = realign_thread_task.delay(thread_id)
    return Response({"task_id": task.id}, status=202)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([UserRateThrottle])
def merge_thread(request, id):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/threads/<id>/merge/",
        DeprecationWarning,
    )
    """Merge another thread into this one."""
    thread = get_object_or_404(NarrativeThread, id=id)
    target_id = request.data.get("target_thread_id")
    if not target_id:
        return Response({"detail": "target_thread_id required"}, status=400)
    target = get_object_or_404(NarrativeThread, id=target_id)

    MemoryEntry.objects.filter(thread=target).update(thread=thread)
    MemoryEntry.objects.filter(narrative_thread=target).update(narrative_thread=thread)
    AssistantThoughtLog.objects.filter(narrative_thread=target).update(
        narrative_thread=thread
    )
    if hasattr(AssistantReflectionLog, "narrative_thread"):
        AssistantReflectionLog.objects.filter(narrative_thread=target).update(
            narrative_thread=thread
        )

    ThreadMergeLog.objects.create(
        from_thread=target, to_thread=thread, summary=request.data.get("summary", "")
    )

    target.delete()

    return Response(NarrativeThreadSerializer(thread).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def split_thread(request, id):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/threads/<id>/split/",
        DeprecationWarning,
    )
    """Split a thread, moving selected entries to a new thread."""
    thread = get_object_or_404(NarrativeThread, id=id)
    from_index = request.data.get("from_index")
    entry_ids = request.data.get("entry_ids")
    if from_index is None and not entry_ids:
        return Response({"detail": "from_index or entry_ids required"}, status=400)

    entries_qs = MemoryEntry.objects.filter(thread=thread).order_by("created_at")
    if from_index is not None:
        try:
            from_index = int(from_index)
        except (TypeError, ValueError):
            return Response({"detail": "from_index must be int"}, status=400)
        entries = list(entries_qs[from_index:])
    else:
        entries = list(entries_qs.filter(id__in=entry_ids))

    new_thread = NarrativeThread.objects.create(title=f"{thread.title} Split")

    moved_ids = []
    for entry in entries:
        entry.thread = new_thread
        entry.narrative_thread = new_thread
        entry.save(update_fields=["thread", "narrative_thread"])
        moved_ids.append(str(entry.id))

    ThreadSplitLog.objects.create(
        original_thread=thread,
        new_thread=new_thread,
        moved_entries=moved_ids,
        summary=request.data.get("summary", ""),
    )

    return Response(NarrativeThreadSerializer(new_thread).data, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def thread_progress(request, id):
    warnings.warn(
        "Deprecated: use /api/v1/mcp/threads/<id>/progress/",
        DeprecationWarning,
    )
    """Return completion progress for a thread and trigger sync."""
    thread = get_object_or_404(NarrativeThread, id=id)

    from mcp_core.tasks.thread_sync import update_thread_progress

    # Sync progress before returning
    update_thread_progress.delay(str(thread.id))
    thread.refresh_from_db()

    data = {
        "completion_status": thread.completion_status,
        "progress_percent": thread.progress_percent,
        "completed_milestones": thread.completed_milestones,
        "completed_at": thread.completed_at,
    }
    return Response(data)
