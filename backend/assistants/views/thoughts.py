from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from assistants.models.assistant import (
    Assistant,
    AssistantChatMessage,
    Topic,
)
from assistants.models.thoughts import AssistantThoughtLog
from assistants.serializers import AssistantThoughtLogSerializer
from mcp_core.serializers_tags import TagSerializer
from django.shortcuts import get_object_or_404
from assistants.utils.session_utils import (
    get_cached_reflection,
    set_cached_reflection,
    get_cached_thoughts,
    set_cached_thoughts,
)
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
from assistants.utils.session_utils import flush_session_to_db
from prompts.utils.mutation import mutate_prompt as run_mutation
from embeddings.helpers.helpers_io import get_embedding_for_text, save_embedding
from assistants.helpers.logging_helper import log_assistant_thought
from mcp_core.models import DevDoc
from assistants.services import AssistantService
from django.http import Http404


class AssistantThoughtViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssistantThoughtLogSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["project", "tags", "created_at"]

    def get_queryset(self):
        assistant = get_object_or_404(Assistant, slug=self.kwargs.get("slug"))
        return AssistantThoughtLog.objects.filter(assistant=assistant).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        page_num = request.query_params.get("page", "1")
        if page_num == "1":
            cache_key = f"{self.kwargs.get('slug')}"
            cached = get_cached_thoughts(cache_key)
            if cached:
                return Response(cached)
            response = super().list(request, *args, **kwargs)
            set_cached_thoughts(cache_key, response.data)
            return response
        return super().list(request, *args, **kwargs)


@api_view(["POST"])
def submit_assistant_thought(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found."}, status=404)

    thought_text = request.data.get("thought", "").strip()
    if not thought_text:
        return Response({"error": "Thought text is required."}, status=400)

    event_id = request.data.get("narrative_event_id")
    event = None
    if event_id:
        from story.models import NarrativeEvent

        event = NarrativeEvent.objects.filter(id=event_id).first()

    log = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=thought_text,
        linked_event=event,
    )

    return Response(
        {
            "thought": log.thought,
            "thought_id": log.id,
            "created_at": log.created_at,
        },
        status=201,
    )



class AssistantThoughtViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssistantThoughtLogSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["created_at", "tags", "project"]
    ordering = ["-created_at"]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        qs = AssistantThoughtLog.objects.filter(assistant__slug=slug)
        return qs.order_by("-created_at")

    def list(self, request, *args, **kwargs):
        page = request.query_params.get("page", "1")
        if page == "1" and len(request.query_params) <= 2:
            key = f"assistant_thoughts_{kwargs['slug']}_p1"
            cached = cache.get(key)
            if cached:
                return Response(cached)
            response = super().list(request, *args, **kwargs)
            cache.set(key, response.data, 300)
            return response
        return super().list(request, *args, **kwargs)


@api_view(["POST"])
def submit_chat_feedback(request):
    uuid = request.data.get("uuid")
    feedback = request.data.get("feedback")
    topic = request.data.get("topic", None)

    try:
        msg = AssistantChatMessage.objects.get(uuid=uuid)
        msg.feedback = feedback
        msg.topic = topic
        msg.save()
        return Response({"success": True})
    except AssistantChatMessage.DoesNotExist:
        return Response({"error": "Message not found"}, status=404)


@api_view(["PATCH"])
def update_message_feedback(request, uuid):
    try:
        msg = AssistantChatMessage.objects.get(uuid=uuid)
    except AssistantChatMessage.DoesNotExist:
        return Response({"error": "Message not found."}, status=404)

    data = request.data
    feedback = data.get("feedback")
    topic_input = data.get("topic")

    if feedback is not None:
        msg.feedback = feedback

    if topic_input:
        # If topic is a string, try to look up or create by name
        if isinstance(topic_input, str):
            topic_obj, _ = Topic.objects.get_or_create(name=topic_input.strip())
            msg.topic = topic_obj
        else:
            # If it's numeric (e.g. ID), fetch normally
            try:
                msg.topic = Topic.objects.get(id=topic_input)
            except Topic.DoesNotExist:
                return Response({"error": "Invalid topic ID"}, status=400)

    msg.save()
    return Response({"success": True})


@api_view(["POST"])
def reflect_on_assistant_thoughts(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found."}, status=404)

    engine = AssistantThoughtEngine(assistant=assistant)
    force_flag = request.data.get("force") or request.query_params.get("force")
    force = str(force_flag).lower() in ["1", "true", "yes"]
    result = engine.reflect_on_thoughts(force=force)

    return Response(result)


@api_view(["GET", "POST"])
def assistant_project_thoughts(request, project_id):
    if request.method == "GET":
        thoughts = AssistantThoughtLog.objects.filter(project_id=project_id).order_by(
            "-created_at"
        )
        assistant_id = request.GET.get("assistant_id")
        if assistant_id:
            thoughts = thoughts.filter(assistant_id=assistant_id)
        serialized = AssistantThoughtLogSerializer(thoughts, many=True)
        return Response(serialized.data)

    elif request.method == "POST":
        project = AssistantService.get_project(project_id)
        if not project:
            return Response({"error": "Project not found."}, status=404)

        thought_text = request.data.get("thought", "")
        if not thought_text.strip():
            return Response({"error": "Thought text is required."}, status=400)

        event_id = request.data.get("narrative_event_id")
        event = None
        if event_id:
            from story.models import NarrativeEvent

            event = NarrativeEvent.objects.filter(id=event_id).first()

        thought = AssistantThoughtLog.objects.create(
            project=project,
            thought=thought_text,
            linked_event=event,
        )

        return Response(
            {
                "thought": thought.thought,
                "thought_id": thought.id,
                "created_at": thought.created_at,
            }
        )


@api_view(["POST"])
def assistant_reflect_on_thoughts(request, project_id):
    project = AssistantService.get_project(project_id)
    if not project:
        return Response({"error": "Project not found."}, status=404)

    engine = AssistantThoughtEngine(assistant=project.assistant, project=project)
    force_flag = request.data.get("force") or request.query_params.get("force")
    force = str(force_flag).lower() in ["1", "true", "yes"]
    result = engine.reflect_on_thoughts(force=force)

    return Response(
        {
            "reflection": result["summary"],
            "trace": result.get("trace", ""),
            "source_count": result.get("source_count", 0),
        }
    )


@api_view(["PATCH"])
def assistant_update_project_thought(request, project_id, thought_id):
    try:
        thought = AssistantThoughtLog.objects.get(id=thought_id, project_id=project_id)
    except AssistantThoughtLog.DoesNotExist:
        return Response({"error": "Thought not found."}, status=404)

    new_text = request.data.get("thought")
    if not new_text:
        return Response({"error": "No thought text provided."}, status=400)

    thought.thought = new_text
    thought.save()

    return Response(
        {
            "message": "Thought updated successfully.",
            "thought_id": thought.id,
            "updated_text": thought.thought,
        }
    )


@api_view(["GET"])
def get_recent_thoughts(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found."}, status=404)

    cached = get_cached_thoughts(slug)
    return Response({"thoughts": cached or []})


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def assistant_reflect_now(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)

    engine = AssistantThoughtEngine(assistant=assistant)
    force_flag = request.data.get("force") or request.query_params.get("force")
    force = str(force_flag).lower() in ["1", "true", "yes"]
    result = engine.reflect_on_thoughts(force=force)

    return Response(
        {
            "assistant": assistant.name,
            "reflection": result["summary"],
            "source_count": result["source_count"],
            "trace": result["trace"],
        }
    )


@api_view(["POST"])
def assistant_dream(request, slug):
    """Trigger dream mode for the assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    topic = request.data.get("topic", "")

    engine = AssistantThoughtEngine(assistant=assistant)
    result = engine.dream(topic)

    return Response({"dream": result.get("thought")})


@api_view(["PATCH"])
def update_reflection_feedback(request, pk):
    try:
        log = AssistantThoughtLog.objects.get(id=pk)
    except AssistantThoughtLog.DoesNotExist:
        return Response({"error": "Thought not found"}, status=404)

    feedback = request.data.get("feedback")
    if feedback:
        log.feedback = feedback
        log.save()
    return Response({"status": "updated", "feedback": log.feedback})


# views/thoughts.py
@api_view(["GET"])
def get_recent_reflections(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    logs = AssistantThoughtLog.objects.filter(assistant=assistant, role="assistant")
    if assistant.current_project_id:
        logs = logs.filter(project_id=assistant.current_project_id)
    logs = logs.order_by("-created_at")[:10]
    data = [
        {
            "id": str(log.id),
            "content": log.thought,
            "timestamp": log.created_at,
            "role": log.role,
            "feedback": log.feedback,
        }
        for log in logs
    ]
    return Response({"thoughts": data})


@api_view(["POST"])
def flush_chat_session_to_log(request, slug):
    from assistants.utils.session_utils import flush_session_to_db

    session_id = request.data.get("session_id")
    if not session_id:
        return Response({"error": "Missing session_id"}, status=400)

    assistant = get_object_or_404(Assistant, slug=slug)
    flushed_count = flush_session_to_db(session_id, assistant)

    return Response(
        {
            "assistant": assistant.name,
            "session_id": session_id,
            "flushed_count": flushed_count,
        }
    )


# /api/assistants/thoughts/<uuid:id>/
@api_view(["GET"])
def assistant_thought_detail(request, id):
    try:
        thought = AssistantThoughtLog.objects.get(id=id)
    except AssistantThoughtLog.DoesNotExist:
        return Response({"error": "Thought not found"}, status=404)

    serializer = AssistantThoughtLogSerializer(thought)
    return Response(serializer.data)


@api_view(["POST"])
def mutate_thought(request, id):
    """Mutate a thought based on feedback style."""
    try:
        thought = AssistantThoughtLog.objects.get(id=id)
    except AssistantThoughtLog.DoesNotExist:
        return Response({"error": "Thought not found"}, status=404)

    style = request.data.get("style", "clarify")

    mutated = run_mutation(thought.thought, style)

    new_log = AssistantThoughtLog.objects.create(
        assistant=thought.assistant,
        project=thought.project,
        linked_memory=thought.linked_memory,
        thought=mutated,
        thought_type="mutation",
        role=thought.role,
        narrative_thread=thought.narrative_thread,
        linked_reflection=thought.linked_reflection,
        parent_thought=thought,
    )
    if thought.tags.exists():
        new_log.tags.set(thought.tags.all())
    if thought.linked_memories.exists():
        new_log.linked_memories.set(thought.linked_memories.all())

    # Optionally embed
    try:
        vector = get_embedding_for_text(mutated)
        if vector:
            save_embedding(new_log, vector)
    except Exception:
        pass

    # Log meta reflection
    if thought.assistant:
        meta_msg = (
            f"Refined thought based on feedback: '{thought.feedback}'. "
            f"Used {style} to improve clarity."
        )
        log_assistant_thought(
            thought.assistant,
            meta_msg,
            project=thought.project,
            thought_type="meta",
        )

    serializer = AssistantThoughtLogSerializer(new_log)
    return Response(serializer.data, status=201)


@api_view(["POST"])
def reflect_on_doc(request):
    doc_id = request.data.get("doc_id")
    assistant_id = request.data.get("assistant_id")
    project_id = request.data.get("project_id")

    if not all([doc_id, assistant_id, project_id]):
        return Response(
            {"error": "doc_id, assistant_id, and project_id required."}, status=400
        )

    try:
        doc = DevDoc.objects.get(id=doc_id)
        assistant = Assistant.objects.get(id=assistant_id)
        project = AssistantService.get_project_or_404(project_id)
    except (DevDoc.DoesNotExist, Assistant.DoesNotExist, Http404) as e:
        return Response({"error": str(e)}, status=404)

    # Simulated AI reflection (you can call GPT later)
    thought = AssistantThoughtLog.objects.create(
        assistant=assistant,
        project=project,
        thought_type="reflection",
        thought=f"🧠 I reflected on '{doc.title}' and it appears to focus on:\n\n{doc.content[:300]}...",
    )

    return Response(
        {
            "id": thought.id,
            "thought": thought.thought,
            "created_at": thought.created_at,
        }
    )


@api_view(["GET"])
def recent_feedback(request, slug):
    """Return last 50 thought logs with feedback."""
    assistant = get_object_or_404(Assistant, slug=slug)
    logs = (
        AssistantThoughtLog.objects.filter(assistant=assistant)
        .exclude(feedback__isnull=True)
        .order_by("-created_at")[:50]
        .select_related("project", "linked_memory")
        .prefetch_related("tags")
    )

    data = [
        {
            "id": str(log.id),
            "thought": log.thought,
            "feedback": log.feedback,
            "created_at": log.created_at,
            "project": str(log.project_id) if log.project_id else None,
            "memory": str(log.linked_memory_id) if log.linked_memory_id else None,
            "tags": TagSerializer(log.tags.all(), many=True).data,
        }
        for log in logs
    ]

    return Response(data)


@api_view(["GET"])
def assistant_thought_map(request, slug):
    """Return thought logs for an assistant with lightweight linkage data."""
    assistant = get_object_or_404(Assistant, slug=slug)

    thoughts = AssistantThoughtLog.objects.filter(assistant=assistant)

    mood = request.GET.get("mood")
    tag = request.GET.get("tag")
    feedback = request.GET.get("feedback")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if mood:
        thoughts = thoughts.filter(mood=mood)
    if tag:
        thoughts = thoughts.filter(tags__slug=tag)
    if feedback:
        thoughts = thoughts.filter(feedback=feedback)
    if start:
        thoughts = thoughts.filter(created_at__gte=start)
    if end:
        thoughts = thoughts.filter(created_at__lte=end)

    thoughts = (
        thoughts.order_by("created_at")
        .select_related(
            "parent_thought",
            "linked_memory",
        )
        .prefetch_related("tags")
    )

    data = [
        {
            "id": str(t.id),
            "thought": t.thought,
            "thought_type": t.thought_type,
            "created_at": t.created_at,
            "mood": t.mood,
            "feedback": t.feedback,
            "parent_thought": str(t.parent_thought_id) if t.parent_thought_id else None,
            "linked_memory": str(t.linked_memory_id) if t.linked_memory_id else None,
            "linked_memory_summary": (
                t.linked_memory.summary if t.linked_memory else None
            ),
            "narrative_thread": (
                str(t.narrative_thread_id) if t.narrative_thread_id else None
            ),
            "tags": list(t.tags.values_list("slug", flat=True)),
        }
        for t in thoughts
    ]

    return Response({"thoughts": data})
