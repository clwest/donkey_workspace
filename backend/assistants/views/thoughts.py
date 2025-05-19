from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from assistants.models import (
    Assistant,
    AssistantThoughtLog,
    AssistantChatMessage,
    Topic,
)
from assistants.serializers import AssistantThoughtLogSerializer
from mcp_core.serializers_tags import TagSerializer
from django.shortcuts import get_object_or_404
from assistants.helpers.redis_helpers import (
    get_cached_reflection,
    set_cached_reflection,
    get_cached_thoughts,
)
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
from assistants.utils.assistant_session import flush_session_to_db
from mcp_core.models import DevDoc
from project.models import Project


@api_view(["POST"])
def submit_assistant_thought(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found."}, status=404)

    thought_text = request.data.get("thought", "").strip()
    if not thought_text:
        return Response({"error": "Thought text is required."}, status=400)

    log = AssistantThoughtLog.objects.create(assistant=assistant, thought=thought_text)

    return Response(
        {
            "thought": log.thought,
            "thought_id": log.id,
            "created_at": log.created_at,
        },
        status=201,
    )


@api_view(["GET"])
def assistant_thoughts_by_slug(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found."}, status=404)

    thoughts = AssistantThoughtLog.objects.filter(assistant=assistant).order_by(
        "-created_at"
    )
    serializer = AssistantThoughtLogSerializer(thoughts, many=True)
    return Response(serializer.data)


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
    result = engine.reflect_on_thoughts()

    return Response(result)


@api_view(["GET", "POST"])
def assistant_project_thoughts(request, project_id):
    if request.method == "GET":
        thoughts = AssistantThoughtLog.objects.filter(project_id=project_id).order_by("-created_at")
        assistant_id = request.GET.get("assistant_id")
        if assistant_id:
            thoughts = thoughts.filter(assistant_id=assistant_id)
        serialized = AssistantThoughtLogSerializer(thoughts, many=True)
        return Response(serialized.data)

    elif request.method == "POST":
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=404)

        thought_text = request.data.get("thought", "")
        if not thought_text.strip():
            return Response({"error": "Thought text is required."}, status=400)

        thought = AssistantThoughtLog.objects.create(
            project=project,
            thought=thought_text,
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
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=404)

    engine = AssistantThoughtEngine(assistant=project.assistant, project=project)
    result = engine.reflect_on_thoughts()

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
    result = engine.reflect_on_thoughts()

    return Response(
        {
            "assistant": assistant.name,
            "reflection": result["summary"],
            "source_count": result["source_count"],
            "trace": result["trace"],
        }
    )


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
    logs = AssistantThoughtLog.objects.filter(
        assistant=assistant, role="assistant"
    )
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
    from assistants.utils.assistant_session import flush_session_to_db

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
        project = Project.objects.get(id=project_id)
    except (DevDoc.DoesNotExist, Assistant.DoesNotExist, Project.DoesNotExist) as e:
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
