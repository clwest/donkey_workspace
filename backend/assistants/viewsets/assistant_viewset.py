from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

import logging
from assistants.models.assistant import Assistant, AssistantRelayMessage
from assistants.models.thoughts import AssistantThoughtLog
from assistants.serializers import (
    AssistantSerializer,
    AssistantRelayMessageSerializer,
    AssistantCreateSerializer,
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
from assistants.helpers.memory_helpers import ensure_welcome_memory
from assistants.models.user_preferences import AssistantUserPreferences
from assistants.serializers import AssistantUserPreferencesSerializer
from assistants.utils.rag_diagnostics import run_assistant_rag_test

logger = logging.getLogger(__name__)
from memory.models import MemoryEntry
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine


class AssistantViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        assistants = Assistant.objects.all()
        order = request.GET.get("order")
        if order == "msi":
            assistants = assistants.order_by("-mood_stability_index")
        serializer = AssistantSerializer(assistants, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create an assistant and indicate if it's the user's first."""
        is_first = not Assistant.objects.filter(created_by=request.user).exists()
        from assistants.serializers import (
            AssistantCreateSerializer,
            AssistantSerializer,
        )

        serializer = AssistantCreateSerializer(data=request.data)
        if serializer.is_valid():
            logger.info("Assistant created by: %s", request.user.id)
            assistant = serializer.save(created_by=request.user)
            AssistantUserPreferences.objects.get_or_create(
                user=request.user, assistant=assistant
            )
            ensure_welcome_memory(assistant)
            if is_first or not request.user.primary_assistant_slug:
                request.user.primary_assistant_slug = assistant.slug
                if not request.user.onboarding_complete:
                    request.user.onboarding_complete = True
                request.user.save(
                    update_fields=["onboarding_complete", "primary_assistant_slug"]
                )
            data = AssistantSerializer(assistant).data
            data["is_first"] = is_first
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        assistant = get_object_or_404(Assistant, slug=pk)
        AssistantUserPreferences.objects.get_or_create(
            user=request.user, assistant=assistant
        )
        ensure_welcome_memory(assistant)
        from assistants.serializers import AssistantDetailSerializer

        serializer = AssistantDetailSerializer(assistant)
        data = serializer.data
        if assistant.current_project:
            from assistants.serializers import ProjectOverviewSerializer

            data["current_project"] = ProjectOverviewSerializer(
                assistant.current_project
            ).data
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

    @action(detail=False, methods=["post"], url_path="primary/create")
    def create_primary(self, request):
        """Create the Primary Orchestrator if missing."""
        assistant = Assistant.objects.filter(is_primary=True).first()
        status_code = status.HTTP_200_OK
        if not assistant:
            from assistants.views.bootstrap import prompt_to_assistant

            assistant = prompt_to_assistant(
                name="Primary Orchestrator",
                tone="strategic",
                personality="intelligent, calm, curious",
            )
            status_code = status.HTTP_201_CREATED

        serializer = AssistantSerializer(assistant)
        return Response(serializer.data, status=status_code)

    @action(detail=False, methods=["post"], url_path="primary/reflect-now")
    def primary_reflect_now(self, request):
        assistant = Assistant.objects.filter(is_primary=True).first()
        if not assistant:
            return Response({"error": "No primary assistant."}, status=404)
        memory_id = request.data.get("memory_id")
        if not memory_id:
            return Response({"error": "memory_id required"}, status=400)
        memory = get_object_or_404(MemoryEntry, id=memory_id)
        if not memory.context:
            memory.context = assistant.memory_context
            memory.save(update_fields=["context"])
        engine = AssistantReflectionEngine(assistant)
        ref_log = engine.reflect_now()
        if not ref_log:
            return Response({"status": "skipped", "summary": ""})
        AssistantThoughtLog.objects.create(
            assistant=assistant,
            thought=ref_log.summary,
            thought_type="reflection",
            linked_memory=memory,
            linked_reflection=ref_log,
        )
        return Response({"status": "ok", "summary": ref_log.summary})

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

    @action(detail=True, methods=["get"], url_path="setup_summary")
    def setup_summary(self, request, pk=None):
        assistant = get_object_or_404(Assistant, slug=pk)
        from assistants.serializers import AssistantSetupSummarySerializer

        serializer = AssistantSetupSummarySerializer(assistant)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        assistant = get_object_or_404(Assistant, slug=pk)
        from assistants.serializers import AssistantPreviewSerializer

        serializer = AssistantPreviewSerializer(assistant)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "patch"], url_path="preferences")
    def preferences(self, request, pk=None):
        """Get or update user preferences for an assistant."""
        assistant = get_object_or_404(Assistant, slug=pk)
        profile, _ = AssistantUserPreferences.objects.get_or_create(
            user=request.user, assistant=assistant
        )
        if request.method == "PATCH":
            serializer = AssistantUserPreferencesSerializer(
                profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = AssistantUserPreferencesSerializer(profile)

        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"], url_path="diagnostics")
    def diagnostics(self, request, pk=None):
        """Return or run RAG diagnostics for an assistant."""
        assistant = get_object_or_404(Assistant, slug=pk)

        if request.method == "POST":
            limit = request.data.get("limit")
            try:
                limit = int(limit) if limit is not None else None
            except (TypeError, ValueError):
                limit = None
            result = run_assistant_rag_test(assistant, limit=limit)
            return Response(result)

        # GET request - provide diagnostic snapshot
        context_id = assistant.memory_context_id
        orphaned_memory_count = MemoryEntry.objects.filter(
            assistant=assistant, context__isnull=True
        ).count()
        reflections_total = AssistantReflectionLog.objects.filter(
            assistant=assistant
        ).count()

        anchors_total = SymbolicMemoryAnchor.objects.count()
        anchors_with_matches = (
            SymbolicMemoryAnchor.objects.filter(chunks__isnull=False)
            .distinct()
            .count()
        )
        anchors_without_matches = anchors_total - anchors_with_matches

        chunks = DocumentChunk.objects.filter(document__linked_assistants=assistant)
        high = chunks.filter(score__gte=0.8).count()
        medium = chunks.filter(score__gte=0.4, score__lt=0.8).count()
        low = chunks.filter(score__lt=0.4).count()

        from memory.models import RAGGroundingLog

        logs = RAGGroundingLog.objects.filter(assistant=assistant)
        glossary_hit_count = logs.filter(glossary_hits__len__gt=0).count()
        fallback_count = logs.filter(fallback_triggered=True).count()

        data = {
            "assistant_id": str(assistant.id),
            "context_id": context_id,
            "orphaned_memory_count": orphaned_memory_count,
            "reflections_total": reflections_total,
            "anchors_total": anchors_total,
            "anchors_with_matches": anchors_with_matches,
            "anchors_without_matches": anchors_without_matches,
            "glossary_hit_count": glossary_hit_count,
            "fallback_count": fallback_count,
            "chunk_score_distribution": {
                "high": high,
                "medium": medium,
                "low": low,
            },
        }
        return Response(data)
