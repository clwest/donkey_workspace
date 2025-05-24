from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

import logging
from assistants.models.assistant import Assistant, AssistantRelayMessage
from assistants.models.thoughts import AssistantThoughtLog
from assistants.serializers import (
    AssistantSerializer,
    AssistantRelayMessageSerializer,
)
from assistants.utils.session_utils import (
    get_cached_thoughts,
    save_message_to_session,
    load_session_messages,
    flush_session_to_db,
)
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
from assistants.utils.delegation import spawn_delegated_assistant
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine

logger = logging.getLogger(__name__)
from memory.models import MemoryEntry
from memory.utils.context_helpers import get_or_create_context_from_memory
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine


class AssistantViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        assistants = Assistant.objects.all()
        order = request.GET.get("order")
        if order == "msi":
            assistants = assistants.order_by("-mood_stability_index")
        serializer = AssistantSerializer(assistants, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = AssistantSerializer(data=request.data)
        if serializer.is_valid():
            assistant = serializer.save()
            return Response(AssistantSerializer(assistant).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        assistant = get_object_or_404(Assistant, slug=pk)
        from assistants.serializers import AssistantDetailSerializer

        serializer = AssistantDetailSerializer(assistant)
        data = serializer.data
        if assistant.current_project:
            from assistants.serializers import ProjectOverviewSerializer

            data["current_project"] = ProjectOverviewSerializer(assistant.current_project).data
        return Response(data)

    @action(detail=False, methods=["get"], url_path="primary")
    def primary(self, request):
        assistant = Assistant.objects.filter(is_primary=True).first()
        if not assistant:
            return Response({"error": "No primary assistant."}, status=404)
        serializer = AssistantSerializer(assistant)
        recent = get_cached_thoughts(assistant.slug) or []
        data = serializer.data
        data["recent_thoughts"] = recent
        return Response(data)

    @action(detail=False, methods=["post"], url_path="primary/reflect-now")
    def primary_reflect_now(self, request):
        assistant = Assistant.objects.filter(is_primary=True).first()
        if not assistant:
            return Response({"error": "No primary assistant."}, status=404)
        memory_id = request.data.get("memory_id")
        if not memory_id:
            return Response({"error": "memory_id required"}, status=400)
        memory = get_object_or_404(MemoryEntry, id=memory_id)
        context = get_or_create_context_from_memory(memory)
        engine = AssistantReflectionEngine(assistant)
        ref_log = engine.reflect_now(context)
        AssistantThoughtLog.objects.create(
            assistant=assistant,
            thought=ref_log.summary,
            thought_type="reflection",
            linked_memory=memory,
            linked_reflection=ref_log,
        )
        return Response({"summary": ref_log.summary})

    @action(detail=False, methods=["post"], url_path="primary/spawn-agent")
    def primary_spawn_agent(self, request):
        parent = Assistant.objects.filter(is_primary=True).first()
        if not parent:
            return Response({"error": "No primary assistant."}, status=404)
        memory_id = request.data.get("memory_id")
        if not memory_id:
            return Response({"error": "memory_id required"}, status=400)
        reason = request.data.get("reason") or request.data.get("goal") or "delegation"
        memory = get_object_or_404(MemoryEntry, id=memory_id)
        child = spawn_delegated_assistant(parent, memory_entry=memory, reason=reason)
        return Response({"child_slug": child.slug})

    @action(detail=True, methods=["post"], url_path="chat")
    def chat(self, request, pk=None):
        assistant = get_object_or_404(Assistant, slug=pk)
        message = request.data.get("message", "")
        session_id = request.data.get("session_id")
        if not session_id:
            return Response({"error": "session_id required"}, status=400)
        save_message_to_session(session_id, "user", message)
        engine = AssistantThoughtEngine(assistant=assistant)
        reply = engine.chat(message)
        save_message_to_session(session_id, "assistant", reply)
        return Response({"reply": reply, "messages": load_session_messages(session_id)})

    @action(detail=True, methods=["post"], url_path="flush-chat")
    def flush_chat(self, request, pk=None):
        assistant = get_object_or_404(Assistant, slug=pk)
        session_id = request.data.get("session_id")
        if not session_id:
            return Response({"error": "session_id required"}, status=400)
        count = flush_session_to_db(session_id, assistant)
        return Response({"flushed": count})

    @action(detail=True, methods=["post"], url_path="relay")
    def relay(self, request, pk=None):
        sender = get_object_or_404(Assistant, slug=pk)
        recipient_slug = request.data.get("recipient_slug")
        message = request.data.get("message")
        if not (recipient_slug and message):
            return Response(
                {"error": "recipient_slug and message required"}, status=400
            )
        recipient = get_object_or_404(Assistant, slug=recipient_slug)
        logger.debug("Creating relay message %s -> %s", sender.slug, recipient.slug)
        relay_msg = AssistantRelayMessage.objects.create(
            sender=sender,
            recipient=recipient,
            content=message,
        )
        relay_msg.mark_delivered()
        logger.debug("Marked delivered %s", relay_msg.id)
        if recipient.auto_reflect_on_message:
            logger.debug("Auto reflecting for %s", recipient.slug)
            engine = AssistantReflectionEngine(recipient)
            try:
                reflection = engine.generate_reflection(
                    f"Incoming message from {sender.name}: {message}"
                )
            except Exception as e:
                logger.warning("Reflection failed: %s", e)
                reflection = message
            log = AssistantThoughtLog.objects.create(
                assistant=recipient,
                thought=reflection,
                role="relay",
                thought_type="reflection",
            )
            relay_msg.mark_responded(thought_log=log)
            logger.debug("Marked responded %s", relay_msg.id)
        serializer = AssistantRelayMessageSerializer(relay_msg)
        return Response(serializer.data, status=201)
