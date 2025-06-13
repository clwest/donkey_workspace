from rest_framework.decorators import (
    api_view,
    permission_classes,
    action,
    throttle_classes,
)
from rest_framework import viewsets
import uuid
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import get_object_or_404
from openai import OpenAI
from utils.llm_router import call_llm
from prompts.utils.token_helpers import EMBEDDING_MODEL
import utils.llm_router as llm_router
from datetime import datetime, timedelta
from django.utils import timezone
import logging
import json
import os
import re
from django.conf import settings
from django.utils.text import slugify
import random
from django.core.management import call_command
from pathlib import Path
from assistants.services import AssistantService
from memory.services import MemoryService
from django.db.models import F
from memory.models import MemoryEntry, RAGGroundingLog
from insights.models import AssistantInsightLog
from assistants.models.user_preferences import AssistantUserPreferences
from utils.rag_debug import log_rag_debug
from memory.serializers import RAGGroundingLogSerializer
from assistants.helpers.logging_helper import (
    log_assistant_thought,
    log_assistant_birth_event,
    reflect_on_birth,
    log_trail_marker,
)
from devtools.models import DevLog
from assistants.helpers.demo_utils import (
    generate_assistant_from_demo,
    get_or_create_usage_for_session,
)

from assistants.models.demo import DemoUsageLog
from assistants.models.demo_usage import DemoSessionLog

from assistants.models.assistant import (
    Assistant,
    TokenUsage,
    ChatSession,
    AssistantMessage,
    AssistantSkill,
    AssistantChatMessage,
    ChatIntentDriftLog,
)
from assistants.models.glossary import SuggestionLog
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.thoughts import AssistantThoughtLog
from prompts.models import PromptMutationLog
from assistants.utils.session_utils import get_cached_thoughts
from assistants.serializers import (
    AssistantSerializer,
    SuggestionLogSerializer,
    DemoComparisonSerializer,
    DriftRefinementLogSerializer,
)
from assistants.utils.session_utils import (
    save_message_to_session,
    flush_session_to_db,
    load_session_messages,
)
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
from assistants.helpers.deletion import cascade_delete_assistant

from assistants.helpers.chat_helper import get_or_create_chat_session, save_chat_message
from assistants.utils.delegation import spawn_delegated_assistant, should_delegate
from assistants.utils.drift_detection import detect_drift_or_miss
from assistants.helpers.memory_helpers import create_memory_from_chat
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from embeddings.helpers.helpers_io import save_embedding, get_embedding_for_text
from embeddings.helpers.helper_tagging import generate_tags_for_memory
from tools.utils import call_tool, reflect_on_tool_output
from tools.utils.tool_registry import execute_tool
from tools.models import Tool, ToolUsageLog
from prompts.models import Prompt
from django.db import models

from intel_core.models import Document, DocumentSet
from mcp_core.models import Tag
from agents.models.lore import SwarmMemoryEntry
from mcp_core.utils.log_prompt import log_prompt_usage
import warnings


logger = logging.getLogger("django")
client = OpenAI()


def extract_speaker_names(text: str):
    """Return a list of potential speaker names found in text."""
    # Optional: Add NLP-based name detection or heuristics
    return []


def _maybe_log_self_doubt(assistant: Assistant, reply: str) -> None:
    """Detect low-confidence replies and log a self-doubt thought."""
    if not reply:
        return
    too_long = len(reply.split()) > 250
    uncertain = "i'm not sure" in reply.lower() or "i am not sure" in reply.lower()
    if too_long or uncertain:
        AssistantThoughtLog.objects.create(
            assistant=assistant,
            thought="Potential low confidence detected in last reply.",
            thought_type="self_doubt",
            clarification_needed=True,
            clarification_prompt="Could you clarify your request?",
        )


class AssistantViewSet(viewsets.ModelViewSet):
    """CRUD operations for :class:`Assistant` objects."""

    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def list(self, request, *args, **kwargs):
        assistants = self.queryset
        order = request.GET.get("order")
        if order == "msi":
            assistants = assistants.order_by("-mood_stability_index")
        min_msi = request.GET.get("min_msi")
        if min_msi is not None:
            try:
                assistants = assistants.filter(mood_stability_index__gte=float(min_msi))
            except ValueError:
                pass
        serializer = self.get_serializer(assistants, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assistant = serializer.save()

        prompt_text = ""
        if assistant.system_prompt:
            prompt_text += assistant.system_prompt.content or ""
        prompt_text += " " + (assistant.specialty or "")
        from assistants.utils.skill_helpers import infer_skills_from_prompt

        skill_data = infer_skills_from_prompt(prompt_text)
        for item in skill_data:
            skill = AssistantSkill.objects.create(
                assistant=assistant,
                name=item["name"],
                confidence=item.get("confidence", 0.5),
                related_tags=item.get("tags", []),
            )
            tools = Tool.objects.filter(
                models.Q(name__icontains=item["name"])
                | models.Q(description__icontains=item["name"])
            )
            if tools.exists():
                skill.related_tools.set(tools)

        headers = self.get_success_headers(serializer.data)
        return Response(
            self.get_serializer(assistant).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def partial_update(self, request, slug=None, *args, **kwargs):
        assistant = get_object_or_404(Assistant, slug=slug)
        if assistant.is_demo:
            return Response({"error": "Demo assistants cannot be modified"}, status=403)
        old_name = assistant.name

        new_name = request.data.get("name")
        new_slug = request.data.get("slug")
        description = request.data.get("description")
        tone = request.data.get("tone")
        preferred_model = request.data.get("preferred_model")
        min_score_threshold = request.data.get("min_score_threshold")
        system_prompt_id = request.data.get("system_prompt")

        if (
            new_slug
            and Assistant.objects.filter(slug=new_slug)
            .exclude(id=assistant.id)
            .exists()
        ):
            return Response({"error": "Slug already exists"}, status=400)

        if new_name is not None:
            assistant.name = new_name

        if new_slug:
            assistant.slug = new_slug

        if description is not None:
            assistant.description = description

        if tone is not None:
            assistant.tone = tone

        if preferred_model is not None:
            assistant.preferred_model = preferred_model

        if min_score_threshold is not None:
            try:
                assistant.min_score_threshold = float(min_score_threshold)
            except (TypeError, ValueError):
                return Response({"error": "Invalid min_score_threshold"}, status=400)

        if system_prompt_id is not None:
            try:
                prompt_obj = Prompt.objects.get(id=system_prompt_id)
            except (ValueError, Prompt.DoesNotExist):
                return Response({"error": "Invalid system_prompt"}, status=400)
            assistant.system_prompt = prompt_obj

        show_intro_splash = request.data.get("show_intro_splash")
        if show_intro_splash is not None:
            assistant.show_intro_splash = bool(show_intro_splash)

        show_trail_recap = request.data.get("show_trail_recap")
        if show_trail_recap is not None:
            assistant.show_trail_recap = bool(show_trail_recap)

        capabilities = request.data.get("capabilities")
        if isinstance(capabilities, dict):
            existing = assistant.capabilities or {}
            existing.update(capabilities)
            assistant.capabilities = existing

        first_personalization = not assistant.memories.filter(type="origin").exists()

        assistant.save()

        if first_personalization and assistant.created_by and assistant.spawned_by:
            log_assistant_birth_event(assistant, assistant.created_by)
            reflect_on_birth(assistant)

        logger.info("Assistant %s edited", assistant.slug)

        if old_name != assistant.name:
            log_assistant_thought(
                assistant,
                f'Assistant renamed from "{old_name}" to "{assistant.name}"',
                thought_type="meta",
            )

        serializer = self.get_serializer(assistant)
        return Response(serializer.data)

    def destroy(self, request, slug=None, *args, **kwargs):
        assistant = Assistant.objects.filter(slug=slug).first()
        if not assistant:
            logger.info("Assistant %s already deleted", slug)
            return Response(status=204)

        if assistant.is_demo:
            return Response({"error": "Demo assistants cannot be deleted"}, status=403)

        qp = request.query_params
        force = qp.get("force") == "true" or request.data.get("force")
        cascade = qp.get("cascade") == "true" or request.data.get("cascade")
        if cascade:
            force = True

        from project.models import Project
        from assistants.models.assistant import ChatSession
        from memory.models import MemoryEntry

        has_live_projects = Project.objects.filter(
            assistant=assistant, status="active"
        ).exists()
        has_children = assistant.sub_assistants.exists()
        if (has_live_projects or has_children) and not force:
            return Response(
                {
                    "error": "Assistant in use",
                    "hint": "Pass force=true or cascade=true",
                },
                status=400,
            )

        if cascade:
            cascade_delete_assistant(assistant)
            logger.info("Assistant %s and children deleted", slug)
            return Response(status=204)

        ChatSession.objects.filter(assistant=assistant).delete()
        Project.objects.filter(assistant=assistant).delete()
        MemoryEntry.objects.filter(assistant=assistant).update(assistant=None)
        MemoryEntry.objects.filter(chat_session__assistant=assistant).update(
            chat_session=None
        )

        assistant.delete()
        logger.info("Assistant %s deleted", slug)
        return Response(status=204)

    def retrieve(self, request, slug=None, *args, **kwargs):
        assistant = get_object_or_404(Assistant, slug=slug)
        from assistants.serializers import (
            AssistantDetailSerializer,
            ProjectOverviewSerializer,
        )

        serializer = AssistantDetailSerializer(assistant)
        data = serializer.data
        if assistant.current_project:
            data["current_project"] = ProjectOverviewSerializer(
                assistant.current_project
            ).data
        return Response(data)

    @action(detail=False, methods=["get"], url_path="primary")
    def primary(self, request):
        user_assistants = Assistant.objects.filter(created_by=request.user)
        if not user_assistants.exists():
            return Response({"detail": "No assistants yet"}, status=204)
        assistant = user_assistants.filter(is_primary=True).first()
        if not assistant:
            return Response({"error": "No primary assistant."}, status=404)

        serializer = AssistantSerializer(assistant)
        recent = get_cached_thoughts(assistant.slug) or []
        data = serializer.data
        data["recent_thoughts"] = recent
        return Response(data)

    @action(detail=False, methods=["post"], url_path="primary/reflect-now")
    def primary_reflect_now(self, request):
        assistant = Assistant.objects.filter(
            created_by=request.user, is_primary=True
        ).first()
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

        log_assistant_thought(
            assistant,
            ref_log.summary,
            thought_type="reflection",
            linked_memory=memory,
            linked_memories=[memory],
            linked_reflection=ref_log,
        )

        return Response({"summary": ref_log.summary})

    @action(detail=False, methods=["post"], url_path="primary/spawn-agent")
    def primary_spawn_agent(self, request):
        parent = Assistant.objects.filter(
            created_by=request.user, is_primary=True
        ).first()
        if not parent:
            return Response({"error": "No primary assistant."}, status=404)

        memory_id = request.data.get("memory_id")
        if not memory_id:
            return Response({"error": "memory_id required"}, status=400)

        reason = request.data.get("reason") or request.data.get("goal") or "delegation"

        memory = get_object_or_404(MemoryEntry, id=memory_id)

        child = spawn_delegated_assistant(parent, memory_entry=memory, reason=reason)

        project = Project.objects.filter(assistant=child).first()

        log_assistant_thought(
            parent,
            f"Spawned {child.name} for {reason}",
            thought_type="planning",
            linked_memory=memory,
            project=project,
        )
        log_assistant_thought(
            child,
            f"Spawned by {parent.name} for {reason}",
            thought_type="meta",
            linked_memory=memory,
            project=project,
        )

        return Response(
            {
                "assistant": {
                    "id": str(child.id),
                    "slug": child.slug,
                    "name": child.name,
                    "tone": child.inherited_tone,
                    "created_from_mood": child.created_from_mood,
                },
                "project_id": str(project.id) if project else None,
            },
            status=201,
        )

    @action(detail=True, methods=["post"], url_path="prepare_creation_from_demo")
    def prepare_creation_from_demo(self, request, slug=None):
        """Return preview info for converting a demo assistant."""
        assistant = get_object_or_404(Assistant, slug=slug, is_demo=True)
        transcript = request.data.get("transcript") or []
        demo_session_id = request.data.get("demo_session_id")
        from assistants.helpers.demo_utils import (
            generate_demo_prompt_preview,
            preview_boost_summary,
            get_origin_traits,
        )

        preview = {
            "assistant": {
                "name": assistant.name,
                "description": assistant.description,
                "tone": assistant.tone,
                "avatar": assistant.avatar,
                "flair": assistant.primary_badge,
                "demo_slug": assistant.demo_slug,
            },
            "recent_messages": transcript[:6],
            "suggested_system_prompt": generate_demo_prompt_preview(assistant),
            "boost_summary": preview_boost_summary(assistant, transcript),
            "origin_traits": get_origin_traits(assistant),
        }
        if demo_session_id:
            from .demo import bump_demo_score

            bump_demo_score(demo_session_id, 10)
        return Response(preview)

    @action(detail=True, methods=["patch"], url_path="assign-primary")
    def assign_primary(self, request, slug=None):
        """Assign this assistant as the system primary."""
        assistant = get_object_or_404(Assistant, slug=slug)
        assistant.is_primary = True
        assistant.save(update_fields=["is_primary"])
        serializer = AssistantSerializer(assistant)
        return Response(serializer.data)

    @action(detail=False, methods=["delete"], url_path="cleanup-unused")
    def cleanup_unused(self, request):
        """Delete assistants with no sessions or projects."""
        from project.models import Project
        from assistants.models.assistant import ChatSession

        qs = (
            Assistant.objects.filter(is_primary=False)
            .annotate(
                has_sessions=models.Exists(
                    ChatSession.objects.filter(assistant=models.OuterRef("pk"))
                )
            )
            .annotate(project_count=models.Count("project"))
        )
        unused = qs.filter(has_sessions=False, project_count=0)
        count = unused.count()
        unused.delete()
        logger.info("cleanup_unused deleted %s assistants", count)
        return Response({"deleted": count})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def assistants_view(request):
    warnings.warn(
        "assistants_view is deprecated; use AssistantViewSet instead",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view({"get": "list", "post": "create"})
    return view(request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_detail_view(request, slug):
    warnings.warn(
        "assistant_detail_view is deprecated; use AssistantViewSet instead",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view(
        {
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }
    )
    return view(request, slug=slug)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def primary_assistant_view(request):
    warnings.warn(
        "primary_assistant_view is deprecated; use AssistantViewSet.primary",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view({"get": "primary"})
    return view(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def primary_reflect_now(request):
    """Trigger immediate reflection for the primary assistant."""
    warnings.warn(
        "primary_reflect_now is deprecated; use AssistantViewSet.primary_reflect_now",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view({"post": "primary_reflect_now"})
    return view(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def primary_spawn_agent(request):
    """Spawn a delegated assistant from memory using the primary assistant."""
    warnings.warn(
        "primary_spawn_agent is deprecated; use AssistantViewSet.primary_spawn_agent",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view({"post": "primary_spawn_agent"})
    return view(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_assistant_from_thought(request):
    data = request.data
    required = [
        "name",
        "description",
        "specialty",
        "prompt_id",
        "project_id",
        # thread_id optional
    ]
    for field in required:
        if field not in data:
            return Response({"error": f"{field} is required"}, status=400)

    try:
        prompt = Prompt.objects.get(id=data["prompt_id"])
    except (ValueError, Prompt.DoesNotExist):
        return Response({"error": "Invalid prompt_id"}, status=400)

    creator_id = data.get("created_by") or (
        request.user.id if request.user and request.user.is_authenticated else None
    )

    if not creator_id:
        return Response({"error": "created_by is required"}, status=400)
    try:
        creator = get_user_model().objects.get(id=creator_id)
    except (ValueError, get_user_model().DoesNotExist):
        return Response({"error": "Invalid created_by"}, status=400)

    project = AssistantService.get_project_or_404(data["project_id"])
    parent_assistant = project.assistant
    thread = project.thread or project.narrative_thread
    thread_id = data.get("thread_id")
    if thread_id:
        thread = AssistantService.get_thread(thread_id) or thread

    base_slug = slugify(data["name"])
    new_assistant = Assistant.objects.filter(slug=base_slug).first()
    if not new_assistant:
        new_assistant = Assistant.objects.create(
            name=data["name"],
            slug=base_slug,
            description=data["description"],
            specialty=data["specialty"],
            system_prompt=prompt,
            created_by=creator,
            preferred_model="gpt-4o",
            parent_assistant=parent_assistant,
            spawn_reason="manual",
            spawned_by=parent_assistant,
        )

    AssistantThoughtLog.objects.create(
        assistant=new_assistant,
        project_id=data["project_id"],
        thought_type="planning",
        thought=f"I created a new assistant: {new_assistant.name}, focused on {new_assistant.specialty}.",
        narrative_thread=thread,
    )

    # Bootstrap project & chat session inheriting the thread
    child_project = AssistantService.create_project(
        user=creator,
        title=f"Auto Project for {new_assistant.name}",
        assistant=new_assistant,
        narrative_thread=thread,
        thread=thread,
        project_type="assistant",
        status="active",
    )
    ChatSession.objects.create(
        assistant=new_assistant,
        project=child_project,
        narrative_thread=thread,
        thread=thread,
        session_id=uuid.uuid4(),
    )

    return Response(
        {
            "id": new_assistant.id,
            "slug": new_assistant.slug,
            "name": new_assistant.name,
        },
        status=201,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assistant_from_documents(request):
    """Create an assistant from one or more Documents."""
    data = request.data
    doc_ids = data.get("document_ids") or []
    if not isinstance(doc_ids, list) or len(doc_ids) == 0:
        return Response({"error": "document_ids required"}, status=400)

    documents = list(Document.objects.filter(id__in=doc_ids))
    if not documents:
        return Response({"error": "Documents not found"}, status=404)

    doc_set = DocumentSet.objects.create(title=f"Ad Hoc Set: {datetime.now().date()}")
    doc_set.documents.set(documents)

    name = data.get("name") or f"{doc_set.title} Assistant"
    personality = data.get("personality", "")
    tone = data.get("tone", "neutral")
    model = data.get("preferred_model", "gpt-4o")

    titles = ", ".join(doc_set.documents.values_list("title", flat=True))

    speaker_names = set()
    for doc in doc_set.documents.all():
        speaker_names.update(extract_speaker_names(doc.content))

    intro = (
        f"You are {name}. Personality: {personality}. Tone: {tone}. "
        f"Specialty: {titles}. "
        "You are allowed to quote from any transcript-based memory if relevant. "
        "When answering questions about speakers, introductions, or source identity, use named context from the memory if available. "
        "You are referencing memory, not accessing video content. "
        "Avoid hallucinated refusals such as 'I can’t access videos' — instead, explain what you find in the transcript memory."
    )
    if speaker_names:
        intro += f" Known speakers include: {', '.join(speaker_names)}."
    codex_prompt = Prompt.objects.create(
        title=f"{name} Codex",
        content=intro,
        type="system",
        tone=tone,
        source="auto",
    )
    summary_prompt = Prompt.objects.create(
        title=f"{name} Summary Seed",
        content="Summarize recent interactions and update memory.",
        type="assistant",
        tone=tone,
        source="auto",
    )
    print("-------------START_SUMMARY_PROMPT-----------------")
    print(summary_prompt)
    print("-------------END_SUMMARY_PROMPT-----------------")
    combined = " ".join((d.summary or d.content[:500]) for d in documents)
    vector = get_embedding_for_text(combined)

    slug_base = slugify(name)
    assistant = Assistant.objects.filter(slug=slug_base).first()
    if not assistant:
        assistant = Assistant.objects.create(
            name=name,
            slug=slug_base,
            specialty=titles[:255],
            personality=personality,
            tone=tone,
            preferred_model=model,
            system_prompt=codex_prompt,
            document_set=doc_set,
            embedding_index={"vector": vector},
            spawn_reason="manual",
        )
    assistant.documents.set(doc_set.documents.all())

    ritual_tags = []
    for slug in ["ritual", "memory-ingestion", "summon"]:
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": slug})
        ritual_tags.append(tag)

    mem = SwarmMemoryEntry.objects.create(
        title=f"Summon {name}",
        content=f"Assistant created from DocumentSet {doc_set.title}",
        origin="summon",
    )
    mem.tags.set(ritual_tags)

    thought = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought_type="meta",
        category="meta",
        thought=f"Assistant summoned from document set {doc_set.title}.",
    )
    thought.tags.set(ritual_tags)

    log_prompt_usage(
        prompt_slug=codex_prompt.slug,
        prompt_title=codex_prompt.title,
        used_by="assistant_from_documents",
        rendered_prompt=codex_prompt.content,
        assistant_id=str(assistant.id),
        extra_data={"document_set": str(doc_set.id)},
    )

    return Response({"assistant_id": str(assistant.id), "slug": assistant.slug})


def _get_demo_starter_memory(assistant):
    """Return pre-seeded chat messages for a demo assistant."""
    mems = MemoryEntry.objects.filter(
        assistant=assistant, is_demo=True, tags__slug="starter-chat"
    ).order_by("created_at")
    messages = []
    for mem in mems:
        text = mem.full_transcript or mem.event or ""
        for line in text.split("\n"):
            if ": " in line:
                role, content = line.split(": ", 1)
                messages.append({"role": role.lower(), "content": content})
    return messages


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_with_assistant_view(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    user = request.user if request.user.is_authenticated else None

    starter_query = request.data.get("starter_query") or request.query_params.get(
        "starter_query"
    )
    inject_flag = request.data.get("inject_starter") or request.query_params.get(
        "inject_starter"
    )
    inject_starter = str(inject_flag).lower() in ["1", "true", "yes"]

    message = request.data.get("message")
    session_id = request.data.get("session_id") or str(uuid.uuid4())
    demo_session_id = request.data.get("demo_session_id")
    history = load_session_messages(session_id)

    should_seed = False
    if starter_query:
        should_seed = True
    if assistant.auto_start_chat and not history:
        should_seed = True
    if inject_starter:
        should_seed = True

    logger.debug(
        "Starter check slug=%s seed=%s query=%s auto_start=%s history=%s inject=%s",
        assistant.slug,
        should_seed,
        bool(starter_query),
        assistant.auto_start_chat,
        bool(history),
        inject_starter,
    )

    starter_messages = (
        _get_demo_starter_memory(assistant) if assistant.is_demo and should_seed else []
    )
    demo_intro_message = None
    if starter_messages:
        first = next((m for m in starter_messages if m["role"] == "assistant"), None)
        if first:
            demo_intro_message = (
                f"{assistant.name} ({assistant.tone}): {first['content']}"
            )

    message = request.data.get("message")
    session_id = request.data.get("session_id") or str(uuid.uuid4())
    demo_session_id = request.data.get("demo_session_id")
    logger.debug(
        "Chat start slug=%s session=%s starter_query=%s starter_memory=%s inject_starter=%s",
        assistant.slug,
        session_id,
        starter_query,
        bool(starter_messages),
        inject_starter,
    )

    injected = False

    if message == "__ping__":
        if assistant.is_demo and demo_session_id:
            log_obj, created = DemoSessionLog.objects.get_or_create(
                session_id=demo_session_id,
                defaults={
                    "assistant": assistant,
                    "starter_query": starter_query or "",
                    "created_from_ip": request.META.get("REMOTE_ADDR", ""),
                    "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
                },
            )
            if created:
                logger.debug("[DemoSession] start %s", demo_session_id)
            usage, u_created = get_or_create_usage_for_session(demo_session_id)
            if u_created:
                logger.debug("[DemoUsage] start %s", demo_session_id)
        if should_seed and starter_query and not history:
            save_message_to_session(session_id, "user", starter_query)
            injected = True
            history = load_session_messages(session_id)
            logger.debug("Injected starter query into session %s", session_id)
        logger.debug(
            "Ping response slug=%s session=%s injected=%s demo_intro=%s",
            assistant.slug,
            session_id,
            injected,
            bool(demo_intro_message),
        )
        return Response(
            {
                "messages": history,
                "starter_memory": starter_messages,
                "demo_intro_message": demo_intro_message,
            }
        )

    if not message:
        return Response({"error": "Empty message."}, status=status.HTTP_400_BAD_REQUEST)

    # Build messages list
    if assistant.system_prompt:
        system_prompt = assistant.system_prompt.content
    else:
        logger.warning("Assistant %s has no system prompt", assistant.slug)
        system_prompt = "You are a helpful assistant."
    if assistant.boost_prompt_in_system and assistant.prompt_notes:
        system_prompt = f"{system_prompt}\n\n{assistant.prompt_notes}".strip()
    identity = assistant.get_identity_prompt()
    if identity:
        system_prompt = f"{system_prompt}\n\n{identity}"
    messages = [{"role": "system", "content": system_prompt}]
    session_history = load_session_messages(session_id)
    messages += session_history
    messages.append({"role": "user", "content": message})

    # Save user message to session
    save_message_to_session(session_id, "user", message)

    # Log internal thought based on user's message
    thought_engine = AssistantThoughtEngine(assistant=assistant)
    thought_engine.think_from_user_message(message)

    chat_session = get_or_create_chat_session(session_id, assistant=assistant)

    if assistant.is_demo and demo_session_id:
        log, created = DemoSessionLog.objects.get_or_create(
            session_id=demo_session_id,
            defaults={
                "assistant": assistant,
                "starter_query": starter_query or "",
                "first_message": message,
                "created_from_ip": request.META.get("REMOTE_ADDR", ""),
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
            },
        )
        if created:
            logger.debug("[DemoSession] start %s", demo_session_id)
        usage, u_created = get_or_create_usage_for_session(demo_session_id)
        if u_created:
            logger.debug("[DemoUsage] start %s", demo_session_id)
        if not created and log.message_count == 0:
            log.first_message = message
        log.message_count = F("message_count") + 1
        log.ended_at = timezone.now()
        log.save()
        from .demo import bump_demo_score

        bump_demo_score(demo_session_id, 1)

    if assistant.is_primary and assistant.live_relay_enabled:
        delegate = assistant.sub_assistants.filter(is_active=True).first()
        if delegate:
            mem = MemoryService.create_entry(
                event=f"Relayed message to {delegate.name}: {message}",
                assistant=delegate,
                related_project=chat_session.project,
                chat_session=chat_session,
                source_role="assistant",
            )
            AssistantMessage.objects.create(
                sender=assistant,
                recipient=delegate,
                content=message,
                session=chat_session,
                related_memory=mem,
            )
    token_usage, _ = TokenUsage.objects.get_or_create(
        session=chat_session,
        defaults={
            "assistant": assistant,
            "user": user,
            "project": chat_session.project,
            "usage_type": "chat",
        },
    )

    tool_slug = request.data.get("tool_slug")
    if tool_slug:
        tool_input = request.data.get("tool_input") or {}
        tool_result = call_tool(tool_slug, tool_input, assistant)
        reflection = reflect_on_tool_output(
            tool_result, tool_slug, tool_input, assistant
        )
        if not reflection.get("useful", True):
            if reflection.get("retry_input"):
                tool_result = call_tool(tool_slug, reflection["retry_input"], assistant)
            else:
                tool_obj = Tool.objects.filter(slug=tool_slug).first()
                delegate = spawn_delegated_assistant(
                    chat_session,
                    reason="tool_unsatisfactory",
                    summary=reflection.get("summary"),
                    triggered_by_tool=tool_obj,
                )
                AssistantThoughtLog.objects.create(
                    assistant=assistant,
                    thought="Delegated due to tool failure",
                    thought_type="reflection",
                    fallback_reason="tool_unsatisfactory",
                    fallback_details={"tool": tool_slug},
                )
                return Response({"delegate_slug": delegate.slug})
        messages.append(
            {"role": "system", "content": f"Tool {tool_slug} output: {tool_result}"}
        )

    if should_delegate(assistant, token_usage, request.data.get("feedback_flag")):
        recent_memory = (
            MemoryService.filter_entries(chat_session=chat_session)
            .order_by("-created_at")
            .first()
        )
        delegate = spawn_delegated_assistant(chat_session, memory_entry=recent_memory)
        return Response({"delegate_slug": delegate.slug})

    # Run LLM chat with optional memory summon
    reply, summoned_ids, rag_meta, reasoning_trace = llm_router.chat(
        messages,
        assistant,
        temperature=0.7,
        auto_expand=not request.data.get("focus_only", True),
        focus_anchors_only=request.data.get("focus_only", True),
        force_chunks=request.query_params.get("force_chunks") == "true",
    )
    if request.query_params.get("debug_chunks") == "true":
        candidates = rag_meta.get("candidates") or rag_meta.get("used_chunks") or []
        for info in candidates[:5]:
            cid = info.get("chunk_id") or info.get("id")
            score = info.get("score") or info.get("final_score")
            text = info.get("text", "")
            logger.info(
                "[ChunkDebug] %s | score=%.4f | len=%d",
                cid,
                float(score or 0.0),
                len(text),
            )
        logger.info(
            "[ChunkDebug] fallback_reason=%s",
            rag_meta.get("fallback_reason"),
        )
    usage = type(
        "U", (), {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    )()
    _maybe_log_self_doubt(assistant, reply)
    tool_result = None
    tool_obj = None
    tool_match = re.match(r"^@tool:(\w+)\s+(\{.*\})", reply)
    if tool_match:
        tool_slug = tool_match.group(1)
        try:
            payload = json.loads(tool_match.group(2))
        except Exception:
            payload = {}
        tool_obj = Tool.objects.filter(slug=tool_slug).first()
        if tool_obj:
            try:
                tool_result = execute_tool(tool_obj, payload)
                ToolUsageLog.objects.create(
                    tool=tool_obj,
                    assistant=assistant,
                    input_payload=payload,
                    output_payload=tool_result,
                    success=True,
                )
                reply = json.dumps(tool_result)
            except Exception as e:
                ToolUsageLog.objects.create(
                    tool=tool_obj,
                    assistant=assistant,
                    input_payload=payload,
                    success=False,
                    error=str(e),
                )
                reply = f"Tool {tool_slug} failed: {e}"

    token_usage.prompt_tokens += getattr(usage, "prompt_tokens", 0)
    token_usage.completion_tokens += getattr(usage, "completion_tokens", 0)
    token_usage.total_tokens += getattr(usage, "total_tokens", 0)
    token_usage.save()

    # Save assistant message
    save_message_to_session(session_id, "assistant", reply)

    if assistant.is_demo:
        history = load_session_messages(session_id)
        if sum(1 for m in history if m.get("role") == "assistant") == 1:
            from assistants.tasks import log_demo_reflection_task

            log_demo_reflection_task.delay(str(assistant.id), session_id)
        logger.debug(
            "Chat response slug=%s session=%s injected=%s demo_intro=%s",
            assistant.slug,
            session_id,
            injected,
            bool(demo_intro_message),
        )
        return Response(
            {
                "messages": history,
                "rag_meta": rag_meta,
                "starter_memory": starter_messages,
                "demo_intro_message": demo_intro_message,
            }
        )

    AssistantThoughtLog.objects.create(
        assistant=assistant,
        project=None,
        thought="Manually testing role override",
        role="user",
        thought_trace="manual",
    )

    # Save chat log
    is_first = not AssistantChatMessage.objects.filter(
        session=chat_session, role="user"
    ).exists()
    drift_score = None
    anchor_matches = []
    if is_first:
        drift_score, anchor_matches = detect_drift_or_miss(message, assistant)
    user_chat = save_chat_message(
        chat_session,
        "user",
        message,
        is_first_user_message=is_first,
        drift_score=drift_score,
        glossary_misses=rag_meta.get("anchor_misses", []),
    )
    assistant_chat = save_chat_message(chat_session, "assistant", reply)
    if is_first:
        ChatIntentDriftLog.objects.create(
            assistant=assistant,
            session=chat_session,
            user_message=user_chat,
            drift_score=drift_score or 0.0,
            matched_anchors=anchor_matches,
            glossary_misses=rag_meta.get("anchor_misses", []),
        )
    engine = AssistantThoughtEngine(assistant=assistant)

    # Save both messages to thought log
    engine.log_thought(message, role="user")
    assist_log = engine.log_thought(
        reply, role="assistant", tool=tool_obj, tool_result=tool_result
    )
    log_obj = assist_log.get("log") if isinstance(assist_log, dict) else None
    if log_obj and summoned_ids:
        log_obj.summoned_memory_ids = summoned_ids
        log_obj.save(update_fields=["summoned_memory_ids"])

    # Save memory entry
    chat_messages = [m for m in messages if m["role"] in ("user", "assistant")]
    chat_transcript = "\n".join(
        [f"{m['role'].capitalize()}: {m['content'].strip()}" for m in chat_messages]
        + [f"Assistant: {reply}"]
    )
    print(f"Chat transcript is {chat_transcript}")
    anchor_slug = None
    if rag_meta.get("anchor_hits"):
        anchor_slug = rag_meta["anchor_hits"][0]

    memory = create_memory_from_chat(
        assistant_name=assistant.name,
        session_id=session_id,
        messages=messages,
        reply=reply,
        importance=5,
        chat_session=chat_session,
        assistant=assistant,
        project=chat_session.project,
        tool_response=tool_result,
        anchor_slug=anchor_slug,
        fallback_reason=rag_meta.get("fallback_reason"),
        is_demo=assistant.is_demo,
    )

    if is_first:
        log_trail_marker(assistant, "first_chat", memory)

    if rag_meta.get("convergence_log_id"):
        from memory.models import AnchorConvergenceLog

        AnchorConvergenceLog.objects.filter(id=rag_meta["convergence_log_id"]).update(
            memory=memory
        )

    # Log thoughts
    log_assistant_thought(assistant, message, thought_type="user", linked_memory=memory)
    log_assistant_thought(
        assistant, reply, thought_type="generated", linked_memory=memory
    )
    user_chat.memory = memory
    assistant_chat.memory = memory
    user_chat.save()
    assistant_chat.save()

    if should_delegate(assistant, token_usage, request.data.get("feedback_flag")):
        delegate = spawn_delegated_assistant(chat_session, memory_entry=memory)
        return Response({"delegate_slug": delegate.slug})

    # Save full transcript once per session
    if not memory.is_conversation:
        history = load_session_messages(session_id)
        full_transcript = "\n\n".join(
            [
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in history
            ]
        )

        memory.full_transcript = full_transcript
        memory.is_conversation = True
        memory.save()

        embed_resp = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=full_transcript,
        )
        embedding_vector = embed_resp.data[0].embedding
        save_embedding(memory, embedding_vector)

    else:
        full_transcript = memory.full_transcript or ""

    tag_names = generate_tags_for_memory(full_transcript) or []
    tag_objs = []
    for name in tag_names:
        norm_name = str(name).strip().lower()
        slug = slugify(norm_name)
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": norm_name})
        tag_objs.append(tag)

    memory.tags.set(tag_objs)
    memory.save()

    if rag_meta.get("anchor_hits") or rag_meta.get("anchor_misses"):
        tag, _ = Tag.objects.get_or_create(
            slug="glossary_insight", defaults={"name": "glossary_insight"}
        )
        memory.tags.add(tag)

    debug_flag = request.query_params.get("debug") or request.data.get("debug")

    should_log = str(debug_flag).lower() == "true" or rag_meta.get(
        "rag_fallback", False
    )
    if should_log:
        RAGGroundingLog.objects.create(
            assistant=assistant,
            query=message,
            used_chunk_ids=[c["chunk_id"] for c in rag_meta.get("used_chunks", [])],
            fallback_triggered=rag_meta.get("rag_fallback", False),
            fallback_reason=rag_meta.get("fallback_reason"),
            glossary_hits=rag_meta.get("anchor_hits", []),
            glossary_misses=rag_meta.get("anchor_misses", []),
            retrieval_score=rag_meta.get("retrieval_score", 0.0),
        )

    prefs = (
        AssistantUserPreferences.objects.filter(user=user, assistant=assistant).first()
        if user
        else None
    )
    reasoning_enabled = prefs.self_narration_enabled if prefs else False
    explanation = None
    if reasoning_enabled:
        from assistants.utils.self_narration import explain_reasoning

        explanation = explain_reasoning(reasoning_trace)
        AssistantInsightLog.objects.create(
            assistant=assistant,
            user=user,
            summary=explanation,
            tags=["self_narration"],
            log_type="self_narration",
        )
    logger.debug(
        "Chat response slug=%s session=%s injected=%s demo_intro=%s",
        assistant.slug,
        session_id,
        injected,
        bool(demo_intro_message),
    )
    resp_data = {
        "messages": load_session_messages(session_id),
        "rag_meta": rag_meta,
        "starter_memory": starter_messages,
        "demo_intro_message": demo_intro_message,
    }
    if reasoning_enabled:
        resp_data["reasoning_trace"] = reasoning_trace
        resp_data["reasoning_explanation"] = explanation
    return Response(resp_data)


@api_view(["POST"])
def flush_chat_session(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    session_id = f"{slug}_default"  # (or pass custom via request)
    saved = flush_session_to_db(session_id, assistant)
    return Response({"archived_count": saved})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_demo_assistants(request):
    """Return all demo assistants using the main serializer."""
    force = request.GET.get("force_seed") == "1"
    assistants = Assistant.objects.filter(is_demo=True).order_by("demo_slug")
    if force or assistants.count() < 3:
        from django.core.management import call_command

        call_command("seed_demo_assistants")
        assistants = Assistant.objects.filter(is_demo=True).order_by("demo_slug")
    for a in assistants:
        if not a.memories.exists():
            from assistants.utils.starter_chat import seed_chat_starter_memory

            seed_chat_starter_memory(a)
    serializer = AssistantSerializer(assistants, many=True)

    data = serializer.data
    rates = []
    for idx, (obj, a) in enumerate(zip(data, assistants)):
        logs = DemoSessionLog.objects.filter(assistant=a)
        total = logs.count()
        conversions = logs.filter(converted_to_real_assistant=True).count()
        bounce = logs.filter(message_count=0).count()
        rate = conversions / total if total else 0
        obj["metrics"] = {
            "total_sessions": total,
            "avg_messages": logs.aggregate(models.Avg("message_count"))[
                "message_count__avg"
            ]
            or 0,
            "conversion_rate": rate,
            "bounce_rate": bounce / total if total else 0,
            "most_common_starter": (
                logs.values("starter_query")
                .annotate(c=models.Count("id"))
                .order_by("-c")
                .first()
            )
            or {},
        }
        if obj["metrics"]["most_common_starter"]:
            obj["metrics"]["most_common_starter"] = obj["metrics"][
                "most_common_starter"
            ]["starter_query"]
        else:
            obj["metrics"]["most_common_starter"] = ""
        obj["is_featured"] = a.is_featured
        obj["featured_rank"] = a.featured_rank
        rates.append((idx, rate))

    top = [r for r in rates if r[1] > 0.25]
    top.sort(key=lambda x: x[1], reverse=True)
    for rank, (idx, _) in enumerate(top[:3], start=1):
        data[idx]["is_featured"] = True
        data[idx]["featured_rank"] = rank

    return Response(data)


# Backwards compatibility alias
demo_assistant = get_demo_assistants


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def demo_usage_overview(request):
    """Return aggregate usage metrics across all demo assistants."""
    logs = DemoSessionLog.objects.all()
    total = logs.count()
    conversions = logs.filter(converted_to_real_assistant=True).count()
    bounce = logs.filter(message_count=0).count()
    top = (
        logs.values("starter_query")
        .annotate(count=models.Count("id"))
        .order_by("-count")[:5]
    )
    return Response(
        {
            "total_sessions": total,
            "avg_session_length": logs.aggregate(models.Avg("message_count"))[
                "message_count__avg"
            ]
            or 0,
            "conversion_rate": conversions / total if total else 0,
            "bounce_rate": bounce / total if total else 0,
            "top_starters": list(top),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def demo_comparison(request):
    """Return a small random set of demo assistants with preview chat."""
    demos = list(Assistant.objects.filter(is_demo=True))
    random.shuffle(demos)
    demos = demos[:3]
    for a in demos:
        if not a.memories.exists():
            from assistants.utils.starter_chat import seed_chat_starter_memory

            seed_chat_starter_memory(a)
    serializer = DemoComparisonSerializer(demos, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assistant_from_demo(request):
    """Clone a demo assistant for the current user."""
    demo_slug = request.data.get("demo_slug")
    transcript = request.data.get("transcript") or []

    session_id = request.data.get("demo_session_id")
    variant = request.data.get("comparison_variant")
    feedback_text = request.data.get("feedback_text")
    rating = request.data.get("rating")

    if not demo_slug:
        return Response({"error": "demo_slug required"}, status=400)

    from assistants.models.demo_usage import DemoSessionLog

    demo_session_id = request.data.get("demo_session_id")
    retain_prompt = str(request.data.get("retain_starter_prompt", "false")).lower() in [
        "1",
        "true",
        "yes",
    ]
    assistant = generate_assistant_from_demo(demo_slug, request.user, transcript)

    if not retain_prompt:
        assistant.system_prompt = None
        assistant.prompt_title = None
        assistant.save(update_fields=["system_prompt", "prompt_title"])
    else:
        original_query = ""
        for msg in transcript:
            if msg.get("role") == "user" and msg.get("content"):
                original_query = msg["content"]
                break
        if not original_query and demo_session_id:
            sess = DemoSessionLog.objects.filter(session_id=demo_session_id).first()
            if sess:
                original_query = sess.starter_query or sess.first_message or ""
        if original_query:
            note = f"Boosted from demo session with query: {original_query}"
            assistant.prompt_notes = (assistant.prompt_notes or "") + "\n" + note
            assistant.save(update_fields=["prompt_notes"])

    mentor_slug = request.data.get("mentor_slug")
    if mentor_slug:
        mentor = Assistant.objects.filter(slug=mentor_slug).first()
        if mentor:
            assistant.mentor_assistant = mentor
            assistant.save(update_fields=["mentor_assistant"])

    boost_summary = None
    if demo_session_id:
        from assistants.helpers.demo_utils import boost_prompt_from_demo

        boost_summary = boost_prompt_from_demo(assistant, transcript)
        DemoUsageLog.objects.filter(session_id=demo_session_id).update(
            converted_to_real_assistant=True,
            user=request.user,
            converted_at=timezone.now(),
            converted_from_demo=timezone.now(),
        )

        from .demo import bump_demo_score

        bump_demo_score(demo_session_id, 10)

    return Response(
        {
            "slug": assistant.slug,
            "demo_slug": demo_slug,
            "boost_summary": boost_summary,
        },
        status=201,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_document_to_assistant(request, slug):
    """Attach an existing Document to an Assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    doc_id = request.data.get("document_id")
    if not doc_id:
        return Response({"error": "document_id required"}, status=400)

    try:
        document = Document.objects.get(id=doc_id)
    except Document.DoesNotExist:
        return Response({"error": "Document not found"}, status=404)

    if assistant.documents.filter(id=document.id).exists():
        return Response({"error": "Document already linked"}, status=400)

    assistant.documents.add(document)

    reflect = str(request.data.get("reflect", "false")).lower() in ["1", "true", "yes"]

    message = f"Linked new document: {document.title}."
    if reflect:
        engine = AssistantReflectionEngine(assistant)
        try:
            engine.reflect_on_document(document)
            message += " Initiated reflection."
        except Exception as e:
            logger.error("Document reflection failed", exc_info=True)

    log_assistant_thought(assistant, message, thought_type="reflection")

    return Response({"assistant": assistant.slug})


@api_view(["POST"])
def review_ingest(request, slug, doc_id):
    """Review a newly ingested document and log insights."""
    assistant = get_object_or_404(Assistant, slug=slug)
    try:
        document = Document.objects.get(id=doc_id)
    except Document.DoesNotExist:
        return Response({"error": "Document not found"}, status=404)

    if not document.chunks.filter(embedding__isnull=False).exists():
        logger.warning("Skipping reflection — no embedded memory found.")
        return Response({"error": "No memory chunks found for reflection."}, status=400)

    if (
        document.last_reflected_at
        and timezone.now() - document.last_reflected_at < timedelta(hours=1)
    ):
        return Response(
            {"status": "skipped", "reason": "Document recently reflected"},
            status=200,
        )

    engine = AssistantReflectionEngine(assistant)
    summary, insights, prompt_obj = engine.reflect_on_document(document)

    if prompt_obj:
        document.generated_prompt = prompt_obj
        document.save(update_fields=["generated_prompt"])

    memory = MemoryEntry.objects.create(
        assistant=assistant,
        document=document,
        event=summary,
        summary=summary,
        type="ingest_review",
    )

    return Response(
        {
            "summary": summary,
            "insights": insights,
            "memory_id": str(memory.id),
            "prompt_id": str(prompt_obj.id) if prompt_obj else None,
            "prompt_title": prompt_obj.title if prompt_obj else None,
        }
    )


@api_view(["POST"])
def self_reflect(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    engine = AssistantReflectionEngine(assistant)
    prompt = f"You are {assistant.name}. Reflect on your recent behavior and suggest updates to your persona_summary, traits, values or motto. Respond with reflection text followed by JSON updates if any."
    try:
        output = engine.generate_reflection(prompt)
    except Exception as e:
        logger.error("Self reflection failed", exc_info=True)
        return Response({"error": "Failed to generate reflection."}, status=500)
    text = output
    updates = {}
    if "{" in output:
        try:
            json_part = output[output.index("{") : output.rindex("}") + 1]
            text = output[: output.index("{")].strip()
            updates = json.loads(json_part)
        except Exception:
            pass
    AssistantReflectionLog.objects.create(
        assistant=assistant,
        summary=text,
        title="Self Reflection",
        category="self_reflection",
        raw_prompt=prompt,
    )
    if updates:
        if updates.get("persona_summary"):
            assistant.persona_summary = updates["persona_summary"]
        if updates.get("traits"):
            assistant.traits = updates["traits"]
        if updates.get("personality_description"):
            assistant.personality_description = updates["personality_description"]
        if updates.get("persona_mode"):
            assistant.persona_mode = updates["persona_mode"]
        if updates.get("values") is not None:
            assistant.values = updates["values"]
        if updates.get("motto"):
            assistant.motto = updates["motto"]
        assistant.save()

    return Response({"summary": text, "updates": updates})


@api_view(["POST"])
def self_assess(request, slug):
    """Run identity alignment assessment for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    system_prompt = assistant.system_prompt.content if assistant.system_prompt else ""
    personality = assistant.personality or ""
    tone = assistant.tone or ""
    recent = AssistantThoughtLog.objects.filter(assistant=assistant).order_by(
        "-created_at"
    )[:20]
    thought_lines = "\n".join(f"- {t.thought}" for t in recent)
    documents = ", ".join(d.title for d in assistant.documents.all()[:5])

    prompt = f"""You are an introspection engine assessing an AI assistant.\n\nSystem Prompt:\n{system_prompt}\n\nPersonality: {personality}\nTone: {tone}\nLinked Documents: {documents}\n\nRecent Thoughts:\n{thought_lines}\n\nAnswer the following questions:\n1. How well does this assistant's recent behavior align with its stated identity?\n2. Are there any signs of drift in tone, personality, or focus?\n3. What refinements to role, tone, or specialties would improve alignment?\n\nRespond in JSON with keys: score, role, prompt_tweaks, summary."""

    try:
        raw = call_llm(
            [{"role": "user", "content": prompt}],
            model=assistant.preferred_model or "gpt-4o",
        )
    except Exception as e:
        logger.error("Self assessment failed", exc_info=True)
        return Response({"error": str(e)}, status=500)

    summary = raw
    details = {}
    if "{" in raw:
        try:
            json_part = raw[raw.index("{") : raw.rindex("}") + 1]
            summary = raw[: raw.index("{")].strip() or summary
            details = json.loads(json_part)
        except Exception:
            details = {}

    log = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=summary,
        thought_type="identity_reflection",
        thought_trace=json.dumps(details),
    )

    response_data = {
        "score": details.get("score"),
        "role": details.get("role"),
        "prompt_tweaks": details.get("prompt_tweaks"),
        "summary": details.get("summary", summary),
        "thought_id": str(log.id),
    }

    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def drift_check(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    from assistants.utils.drift_detection import analyze_drift_for_assistant
    from assistants.serializers import SpecializationDriftLogSerializer

    log = analyze_drift_for_assistant(assistant)
    data = {
        "drift": log is not None,
        "log": SpecializationDriftLogSerializer(log).data if log else None,
    }
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refine_from_drift(request, slug):
    """Suggest glossary and prompt fixes based on drift logs."""
    assistant = get_object_or_404(Assistant, slug=slug)
    session_id = request.data.get("session_id")
    overrides = request.data.get("overrides") or {}

    glossary_map: dict[str, str] = {}
    if session_id:
        from memory.models import RAGPlaybackLog

        logs = RAGPlaybackLog.objects.filter(
            assistant=assistant, demo_session_id=str(session_id)
        ).order_by("created_at")
        for pb in logs:
            if any(c.get("is_fallback") for c in pb.chunks):
                term = (pb.query_term or pb.query).strip().lower()
                if term and term not in glossary_map:
                    glossary_map[term] = "fallback"

    glossary_fixes = [
        {"term": t, "cause": glossary_map[t]} for t in sorted(glossary_map.keys())
    ]

    prompt_before = assistant.system_prompt.content if assistant.system_prompt else ""
    prompt_after = prompt_before
    if overrides.get("revise_prompt"):
        from assistants.utils.recovery import create_prompt_revision

        new_prompt = create_prompt_revision(assistant)
        if new_prompt:
            prompt_after = new_prompt.content

    tone_tags = []
    if overrides.get("tone") and overrides.get("tone") != assistant.tone:
        tone_tags.append("tone-mismatch")

    from assistants.utils.drift_diagnosis import analyze_drift_symptoms

    drift = analyze_drift_symptoms(str(session_id)) if session_id else None

    if glossary_fixes or tone_tags:
        from assistants.models.assistant import AssistantDriftRefinementLog

        AssistantDriftRefinementLog.objects.create(
            assistant=assistant,
            session_id=str(session_id) if session_id else "",
            glossary_terms=glossary_fixes,
            prompt_sections=[],
            tone_tags=tone_tags,
        )

    return Response(
        {
            "drift": drift,
            "glossary_fixes": glossary_fixes,
            "prompt_revision": (
                {"before": prompt_before, "after": prompt_after}
                if prompt_before != prompt_after
                else None
            ),
            "tone_tags": tone_tags,
        }
    )


@api_view(["POST"])
def recover_assistant_view(request, slug):
    """Run a lightweight recovery routine for the assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    from assistants.utils.recovery import (
        create_prompt_revision,
        generate_recovery_summary,
    )
    from intel_core.management.commands.fix_doc_progress import (
        Command as FixDocProgressCommand,
    )
    from assistants.utils.chunk_retriever import get_relevant_chunks
    from prompts.utils.openai_utils import reflect_on_prompt
    from assistants.utils.assistant_reflection_engine import (
        AssistantReflectionEngine,
    )
    from memory.models import MemoryEntry

    summary = generate_recovery_summary(assistant)
    prompt_tip = reflect_on_prompt(summary)
    create_prompt_revision(assistant)

    repaired_docs = []
    cmd = FixDocProgressCommand()
    cmd.stdout = open(os.devnull, "w")
    cmd.stderr = open(os.devnull, "w")
    engine = AssistantReflectionEngine(assistant)
    for doc in assistant.assigned_documents.all():
        result = cmd.handle(doc_id=str(doc.id), repair=True)
        repaired_docs.append({"id": str(doc.id), "result": result})
        try:
            summary, _ins, _p = engine.reflect_on_document(doc)
            MemoryEntry.objects.create(
                assistant=assistant,
                document=doc,
                context=assistant.memory_context,
                event=summary,
                summary=summary,
                full_transcript=summary,
                type="recovered",
            )
        except Exception as e:
            logger.exception("[Recovery] Reflection failed for %s", doc.title)

    rag_replay = None
    log_path = Path(settings.BASE_DIR) / "static" / "rag_failures.json"
    if log_path.exists():
        try:
            with open(log_path) as f:
                entries = json.load(f)
            for entry in reversed(entries):
                if entry.get("assistant") == assistant.slug:
                    query = entry.get("query", "")
                    expected = entry.get("expected_chunks", [])
                    chunks, reason, *_ = get_relevant_chunks(
                        assistant.slug,
                        query,
                        memory_context_id=(
                            str(assistant.memory_context_id)
                            if assistant.memory_context_id
                            else None
                        ),
                        debug=True,
                    )
                    used = [c.get("chunk_id") for c in chunks]
                    rag_replay = {
                        "query": query,
                        "expected": expected,
                        "used": used,
                        "reason": reason,
                    }
                    break
        except Exception:
            rag_replay = None

    assistant.needs_recovery = False
    assistant.save(update_fields=["needs_recovery"])

    AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=f"Recovery run: {summary}",
        thought_type="reflection",
        category="meta",
    )

    return Response(
        {
            "summary": summary,
            "prompt_suggestion": prompt_tip,
            "doc_repairs": repaired_docs,
            "rag_replay": rag_replay,
        }
    )


@api_view(["POST"])
def reflect_on_assistant(request):
    """
    POST /api/assistants/thoughts/reflect_on_assistant/
    Body: {
        "assistant_id": str,
        "project_id": str,
        "reason": str (optional)
    }
    """
    assistant_id = request.data.get("assistant_id")
    project_id = request.data.get("project_id")
    reason = request.data.get("reason", "")

    if not assistant_id or not project_id:
        return Response(
            {"error": "assistant_id and project_id are required."}, status=400
        )

    try:
        assistant = Assistant.objects.get(id=assistant_id)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found."}, status=404)

    project = AssistantService.get_project(project_id)
    if not project:
        return Response({"error": "Project not found."}, status=404)

    creator = assistant.created_by

    # === Compose Reflection Prompt ===
    context = f"""
    You are Zeno the Build Wizard, reflecting on a new assistant you created.
    
    Assistant Name: {assistant.name}
    Specialty: {assistant.specialty or "(unspecified)"}
    Description: {assistant.description or "(none)"}
    Model: {assistant.preferred_model or "default"}
    Prompt ID: {assistant.system_prompt_id or "n/a"}

    Reason for Creation: {reason or "(not provided)"}

    Please write a short, clear reflection on:
    - Whether the assistant's purpose is well defined
    - Whether its system prompt or tone should be adjusted
    - Any improvements you recommend

    Format:
    Reflection on assistant: {assistant.name}
    [Your thoughts here]
    """

    client = OpenAI()
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.5,
            messages=[
                {"role": "system", "content": "You are a concise reflection engine."},
                {"role": "user", "content": context},
            ],
        )
        thought_text = completion.choices[0].message.content.strip()
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    # Log the reflection under Zeno or creator
    AssistantThoughtLog.objects.create(
        assistant=creator,
        project=project,
        thought=thought_text,
        thought_type="reflection",
    )

    return Response(
        {"message": "Reflection logged.", "thought": thought_text}, status=201
    )


@api_view(["POST"])
def clarify_prompt(request, slug):
    """Trigger prompt clarification for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    text = request.data.get("text")
    if not text:
        return Response({"error": "text required"}, status=400)

    from prompts.utils.mutation import mutate_prompt
    from prompts.utils.openai_utils import reflect_on_prompt

    clarified = mutate_prompt(text, "clarify")

    PromptMutationLog.objects.create(
        original_prompt=assistant.system_prompt,
        mutated_text=clarified,
        mode="clarify",
    )

    thought_text = reflect_on_prompt(text)
    thought = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=thought_text,
        thought_type="prompt_clarification",
        clarification_needed=False,
    )

    return Response({"clarified": clarified, "thought_id": str(thought.id)})


@api_view(["GET"])
def failure_log(request, slug):
    """Return thought logs marked with self doubt or needing clarification."""
    assistant = get_object_or_404(Assistant, slug=slug)
    logs = AssistantThoughtLog.objects.filter(assistant=assistant).filter(
        models.Q(thought_type="self_doubt") | models.Q(clarification_needed=True)
    )
    data = [
        {
            "id": str(l.id),
            "text": l.thought,
            "created_at": l.created_at,
            "clarification_prompt": l.clarification_prompt,
        }
        for l in logs
    ]
    return Response(data)


from api.throttles import HeavyRateThrottle


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@throttle_classes([HeavyRateThrottle])
def rag_grounding_logs(request, slug):
    """Return recent RAG grounding logs for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from utils.rag_debug import get_recent_logs

    qs = get_recent_logs(assistant)
    if request.GET.get("fallback") == "true":
        qs = qs.filter(fallback_triggered=True)
    score_lt = request.GET.get("score_lt")
    if score_lt:
        try:
            qs = qs.filter(retrieval_score__lt=float(score_lt))
        except ValueError:
            pass
    logs = qs[:50]
    data = RAGGroundingLogSerializer(logs, many=True).data
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def rag_drift_report(request, slug):
    """Return aggregated fallback scores for glossary anchors."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from django.db.models import Avg, Count, Max
    from memory.models import RAGGroundingLog

    qs = RAGGroundingLog.objects.filter(
        assistant=assistant, fallback_triggered=True
    ).exclude(expected_anchor="")

    stats = (
        qs.values("expected_anchor")
        .annotate(avg=Avg("adjusted_score"), count=Count("id"))
        .order_by("expected_anchor")
    )

    data = []
    for row in stats:
        anchor = row["expected_anchor"]
        avg_score = round(row["avg"] or 0.0, 2)
        fallback_count = row["count"]
        last = qs.filter(expected_anchor=anchor).order_by("-created_at").first()
        last_chunk = last.used_chunk_ids[0] if last and last.used_chunk_ids else None
        if avg_score < 0.2 and fallback_count >= 3:
            risk = "high"
        elif 0.2 <= avg_score <= 0.6:
            risk = "medium"
        else:
            risk = "healthy"
        data.append(
            {
                "term": anchor,
                "avg_score": avg_score,
                "fallback_count": fallback_count,
                "last_chunk_id": last_chunk,
                "risk": risk,
            }
        )

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def first_question_stats(request, slug):
    """Return summary stats about first user questions."""
    assistant = get_object_or_404(Assistant, slug=slug)
    logs = ChatIntentDriftLog.objects.filter(assistant=assistant)
    from django.db.models import Count, Avg

    summary = (
        logs.values("user_message__content").annotate(c=Count("id")).order_by("-c")[:5]
    )
    drift_avg = logs.aggregate(avg=Avg("drift_score"))["avg"] or 0.0
    return Response(
        {
            "top_questions": [
                {"text": row["user_message__content"], "count": row["c"]}
                for row in summary
            ],
            "avg_drift": round(drift_avg, 2),
            "total": logs.count(),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def anchor_health(request, slug):
    """Return glossary anchor health metrics for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from memory.services.anchor_health import get_anchor_health_metrics

    status = request.GET.get("status")
    metrics = get_anchor_health_metrics(assistant)

    if status == "high_drift":
        metrics = [m for m in metrics if m["drift_score"] >= 0.5]
    elif status == "no_match":
        metrics = [
            m for m in metrics if m["avg_score"] < 0.2 and m["fallback_count"] > 0
        ]
    elif status == "pending_mutation":
        metrics = [m for m in metrics if m["mutation_status"] == "pending"]

    return Response({"results": metrics})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def drift_heatmap(request, slug):
    """Return aggregated reflection drift data for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from utils.reflection_drift import aggregate_drift_by_anchor

    days = request.GET.get("days")
    try:
        days = int(days) if days else None
    except ValueError:
        days = None

    results = aggregate_drift_by_anchor(assistant, days)
    return Response({"results": results})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def drift_fixes(request, slug):
    """Return recent drift refinement logs for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    qs = assistant.drift_refinement_logs.all()
    log_type = request.GET.get("type")
    if log_type == "glossary":
        qs = qs.exclude(glossary_terms=[])
    elif log_type == "prompt":
        qs = qs.exclude(prompt_sections=[])
    elif log_type == "tone":
        qs = qs.exclude(tone_tags=[])
    since = request.GET.get("since")
    if since:
        try:
            since_dt = timezone.datetime.fromisoformat(since)
            qs = qs.filter(created_at__gte=since_dt)
        except ValueError:
            pass
    if request.GET.get("demo_only") == "true":
        qs = qs.filter(assistant__is_demo=True)
    logs = qs.order_by("-created_at")[:50]
    if not logs:
        return Response({"results": [], "detail": "no refinement logs found"})
    data = DriftRefinementLogSerializer(logs, many=True).data
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def glossary_stats(request, slug):
    """Return acquisition stage counts for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from django.db.models import Count
    from memory.models import SymbolicMemoryAnchor

    qs = SymbolicMemoryAnchor.objects.filter(memory_context=assistant.memory_context)
    stage_counts = qs.values("acquisition_stage").annotate(count=Count("id"))
    result = {"reinforced": 0, "acquired": 0, "exposed": 0, "unseen": 0}
    for row in stage_counts:
        stage = row["acquisition_stage"] or "unseen"
        result[stage] = row["count"]
    return Response(result)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def glossary_convergence(request, slug):
    """Return glossary convergence metrics for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from django.db.models import Avg, Count
    from django.utils import timezone
    from datetime import timedelta
    from memory.models import SymbolicMemoryAnchor, RAGGroundingLog

    anchors = SymbolicMemoryAnchor.objects.filter(
        memory_context=assistant.memory_context
    )
    total = anchors.count()

    logs = RAGGroundingLog.objects.filter(assistant=assistant).exclude(
        expected_anchor=""
    )
    grounded_slugs = (
        logs.filter(fallback_triggered=False)
        .values_list("expected_anchor", flat=True)
        .distinct()
    )
    grounded = anchors.filter(slug__in=grounded_slugs).count()
    failing = total - grounded

    now = timezone.now()
    mutated_recently = anchors.filter(
        created_at__gte=now - timedelta(days=7),
        mutation_source__isnull=False,
    ).count()
    inferred_recently = anchors.filter(
        source="memory_inferred",
        created_at__gte=now - timedelta(days=7),
    ).count()

    stats = []
    for a in anchors:
        qs = logs.filter(expected_anchor=a.slug)
        avg = qs.aggregate(avg=Avg("adjusted_score"))["avg"] or 0.0
        fallbacks = qs.filter(fallback_triggered=True).count()
        last = qs.order_by("-created_at").first()
        last_chunk = last.used_chunk_ids[0] if last and last.used_chunk_ids else None
        slogs = list(qs.order_by("-created_at")[:2])
        change = "➖"
        if len(slogs) >= 2:
            diff = (slogs[0].adjusted_score or 0) - (slogs[1].adjusted_score or 0)
            if diff > 0:
                change = "⬆️"
            elif diff < 0:
                change = "⬇️"
        risk = "low"
        if avg < 0.2 and fallbacks >= 3:
            risk = "high"
        elif 0.2 <= avg <= 0.6:
            risk = "medium"
        status = "healthy" if a.slug in grounded_slugs else "failing"
        stats.append(
            {
                "label": a.label,
                "status": status,
                "mutation_source": a.mutation_source,
                "mutation_status": a.mutation_status,
                "avg_score": round(avg, 2),
                "fallbacks": fallbacks,
                "last_used_chunk": last_chunk,
                "change": change,
                "risk": risk,
            }
        )

    convergence = (grounded / total * 100) if total else 0

    return Response(
        {
            "total_anchors": total,
            "grounded": grounded,
            "failing": failing,
            "mutated_recently": mutated_recently,
            "inferred_recently": inferred_recently,
            "convergence_score": round(convergence, 1),
            "anchor_stats": stats,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def boost_anchors(request, slug):
    """Boost glossary anchors for an assistant."""
    get_object_or_404(Assistant, slug=slug)
    terms = request.data.get("terms", [])
    if not isinstance(terms, list):
        terms = [terms]
    boost = float(request.data.get("boost", 0.1))
    from utils.rag_debug import boost_glossary_anchor

    boosted = []
    for term in terms:
        boost_glossary_anchor(term, boost)
        boosted.append(term)
    return Response({"boosted": boosted, "boost": boost})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def suggest_glossary_anchor(request, slug):
    """Proxy anchor suggestion to intel debug view with assistant context."""
    get_object_or_404(Assistant, slug=slug)
    from intel_core.views import debug as debug_views

    return debug_views.suggest_glossary_anchor(request)


@api_view(["GET"])
def assistant_lineage(request, slug):
    """Return a recursive lineage tree for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    def build_tree(node):
        return {
            "id": str(node.id),
            "name": node.name,
            "children": [build_tree(c) for c in node.sub_assistants.all()],
        }

    return Response(build_tree(assistant))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def clean_memories(request, slug):
    """Purge weak recent memories for an assistant."""
    call_command("clean_recent_memories", assistant=slug)
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def clean_projects(request, slug):
    """Remove stale assistant projects."""
    call_command("clean_linked_projects", assistant=slug)
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def patch_drifted_reflections(request, slug):
    """Patch reflection summaries that drifted after glossary updates."""
    limit = request.data.get("limit")
    kwargs = {"assistant": slug}
    if limit:
        kwargs["limit"] = limit
    call_command("patch_reflection_summaries", **kwargs)
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def retry_birth_reflection(request, slug):
    """Retry a failed birth reflection for an assistant."""
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        assistant = get_object_or_404(Assistant, id=slug)

    if assistant.last_reflection_successful:
        return Response({"error": "Reflection already completed"}, status=400)
    if not assistant.can_retry_birth_reflection:
        return Response({"error": "Retry disabled"}, status=400)

    reflect_on_birth(assistant)
    assistant.birth_reflection_retry_count += 1
    if not assistant.last_reflection_successful and assistant.birth_reflection_retry_count >= 3:
        assistant.can_retry_birth_reflection = False
    if assistant.last_reflection_successful:
        assistant.can_retry_birth_reflection = False
    assistant.save(
        update_fields=[
            "birth_reflection_retry_count",
            "can_retry_birth_reflection",
        ]
    )
    DevLog.objects.create(
        event="birth_reflection_retry",
        assistant=assistant,
        success=assistant.last_reflection_successful,
        details=assistant.reflection_error or "",
    )
    return Response(AssistantSerializer(assistant).data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def seed_chat_memory(request, slug):
    """Reseed starter chat memories for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from assistants.utils.starter_chat import seed_chat_starter_memory

    mems = seed_chat_starter_memory(assistant)
    return Response({"created": [str(m.id) for m in mems]})


@api_view(["POST"])
def reset_demo_assistant(request, slug):
    """Reset a demo assistant's memories."""
    force_seed = request.GET.get("force_seed") == "true"
    assistant = Assistant.objects.filter(slug=slug, is_demo=True).first()
    if not assistant and force_seed:
        from django.core.management import call_command

        call_command("seed_demo_assistants")
        assistant = get_object_or_404(Assistant, slug=slug, is_demo=True)
    elif not assistant:
        return Response(status=404)

    from assistants.utils.starter_chat import reset_demo_memory

    mems = reset_demo_memory(assistant)
    return Response({"status": "reset", "created": [str(m.id) for m in mems]})


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def demo_feedback(request):
    """Record demo feedback or list existing submissions."""
    from assistants.models.demo import DemoUsageLog
    from assistants.models.demo_usage import DemoSessionLog

    if request.method == "POST":
        session_id = request.data.get("session_id")
        feedback_text = request.data.get("feedback_text")
        rating = request.data.get("rating")
        if not session_id:
            return Response({"error": "session_id required"}, status=400)

        log, _ = DemoUsageLog.objects.get_or_create(
            session_id=session_id,
            defaults={"demo_slug": request.data.get("demo_slug", "")},
        )
        if feedback_text:
            log.feedback_text = feedback_text
        if rating:
            try:
                log.user_rating = int(rating)
            except (TypeError, ValueError):
                pass
        log.feedback_submitted = True
        log.save()
        return Response({"status": "ok"})

    qs = DemoUsageLog.objects.all().order_by("-created_at")

    rating = request.GET.get("rating")
    if rating:
        try:
            qs = qs.filter(user_rating=int(rating))
        except (TypeError, ValueError):
            pass

    demo_slug = request.GET.get("demo_slug")
    if demo_slug:
        qs = qs.filter(demo_slug=demo_slug)

    converted = request.GET.get("converted")
    if converted is not None:
        val = str(converted).lower() in ["1", "true", "yes"]
        ids = DemoSessionLog.objects.filter(
            converted_to_real_assistant=val
        ).values_list("session_id", flat=True)
        qs = qs.filter(session_id__in=list(ids))

    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(qs, request)

    session_map = {
        s.session_id: s
        for s in DemoSessionLog.objects.filter(
            session_id__in=[log.session_id for log in page]
        )
    }

    data = []
    for log in page:
        sess = session_map.get(log.session_id)
        data.append(
            {
                "id": log.id,
                "demo_slug": log.demo_slug,
                "session_id": log.session_id,
                "rating": log.user_rating,
                "feedback_text": log.feedback_text,
                "interaction_score": getattr(sess, "demo_interaction_score", 0),
                "converted": getattr(sess, "converted_to_real_assistant", False),
                "message_count": getattr(sess, "message_count", 0),
                "timestamp": log.created_at,
                "starter_query": getattr(sess, "starter_query", ""),
                "helpful_tips": getattr(sess, "tips_helpful", 0),
            }
        )

    return paginator.get_paginated_response(data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def clear_demo_feedback(request):
    """Delete all demo feedback logs (admin only)."""
    from assistants.models.demo import DemoUsageLog
    from assistants.models.demo_usage import DemoSessionLog

    DemoUsageLog.objects.all().delete()
    DemoSessionLog.objects.all().delete()
    try:
        from assistants.models.demo_feedback import DemoFeedbackLog

        DemoFeedbackLog.objects.all().delete()
    except Exception:
        pass

    return Response({"status": "cleared"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def run_check_demo_seed(request):
    """Run the check_demo_seed management command."""
    from io import StringIO

    out = StringIO()
    call_command("check_demo_seed", stdout=out)
    return Response({"output": out.getvalue()})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def drift_suggestions(request, slug):
    """List or refresh drift-based glossary suggestions."""
    assistant = get_object_or_404(Assistant, slug=slug)
    if request.method == "POST":
        call_command("review_first_message_drift", assistant=slug)
        return Response({"status": "queued"})

    qs = SuggestionLog.objects.filter(assistant=assistant, status="pending")
    anchor = request.GET.get("anchor")
    severity = request.GET.get("severity")
    if anchor:
        qs = qs.filter(anchor_slug=anchor)
    if severity:
        try:
            qs = qs.filter(score__gte=float(severity))
        except ValueError:
            pass
    qs = qs.order_by("-created_at")
    serializer = SuggestionLogSerializer(qs, many=True)
    return Response({"results": serializer.data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_summary(request, slug):
    """Return high-level metrics for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from assistants.serializers import AssistantOverviewSerializer

    serializer = AssistantOverviewSerializer(assistant)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_trust_profile(request, slug):
    """Return trust and signal metrics for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from assistants.serializers import AssistantOverviewSerializer
    from assistants.models.assistant import AssistantDriftRefinementLog
    from assistants.models.reflection import AssistantReflectionLog
    from memory.models import RAGGroundingLog
    from assistants.utils.trust_profile import update_assistant_trust_cache

    overview = AssistantOverviewSerializer(assistant).data
    trust = update_assistant_trust_cache(assistant)

    last_reflection = (
        AssistantReflectionLog.objects.filter(assistant=assistant)
        .order_by("-created_at")
        .values_list("created_at", flat=True)
        .first()
    )

    drift_fix_count = AssistantDriftRefinementLog.objects.filter(
        assistant=assistant
    ).count()

    logs = RAGGroundingLog.objects.filter(assistant=assistant).values(
        "glossary_hits",
        "glossary_misses",
    )
    hits = 0
    misses = 0
    for row in logs:
        hits += len(row.get("glossary_hits") or [])
        misses += len(row.get("glossary_misses") or [])
    ratio = hits / (hits + misses) if (hits + misses) else 0.0

    first_reflection = (
        AssistantReflectionLog.objects.filter(assistant=assistant)
        .order_by("created_at")
        .values_list("created_at", flat=True)
        .first()
    )
    data = {
        **overview,
        "trust_score": trust["score"],
        "trust_level": trust["level"],
        "score_components": trust["components"],
        "last_reflection_at": last_reflection,
        "first_reflection_at": first_reflection,
        "drift_fix_count": drift_fix_count,
        "glossary_hit_ratio": round(ratio, 2),
        "badge_labels": assistant.skill_badges or [],
    }
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_primary_assistant_view(request):
    """Create the primary assistant for the requesting user."""
    view = AssistantViewSet.as_view({"post": "create_primary"})
    return view(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_nurture(request, slug):
    """Begin nurture flow for a demo-cloned assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    if assistant.nurture_started_at:
        return Response({"status": "already_started"})
    assistant.nurture_started_at = timezone.now()
    assistant.save(update_fields=["nurture_started_at"])
    from assistants.helpers.logging_helper import log_trail_marker

    log_trail_marker(assistant, "nurture_started")
    return Response({"status": "ok"})


@api_view(["GET"])
def default_template(request):
    """Return starter assistant template data based on onboarding."""
    user = request.user
    from memory.models import SymbolicMemoryAnchor

    latest = Assistant.objects.filter(created_by=user).order_by("-created_at").first()
    name = (latest.name if latest else user.assistant_name) or "My Assistant"
    description = (latest.description if latest else user.goals) or ""
    personality = (
        latest.personality
        if latest and latest.personality
        else user.assistant_personality
    ) or "helpful"
    tone = latest.tone if latest and latest.tone else "friendly"
    anchors = (
        SymbolicMemoryAnchor.objects.filter(
            models.Q(memories__source_user=user) | models.Q(assistant__created_by=user)
        )
        .distinct()
        .order_by("slug")[:3]
    )
    starter_terms = [
        {"slug": a.slug, "label": a.label, "description": a.description}
        for a in anchors
    ]
    demo_clone = (
        Assistant.objects.filter(created_by=user, is_demo_clone=True)
        .select_related("spawned_by")
        .order_by("-created_at")
        .first()
    )
    mentor = None
    if demo_clone and demo_clone.spawned_by:
        mentor = {
            "demo_slug": demo_clone.spawned_by.demo_slug,
            "name": demo_clone.spawned_by.name,
        }
    return Response(
        {
            "name": name,
            "description": description,
            "personality": personality,
            "tone": tone,
            "starter_terms": starter_terms,
            "mentor": mentor,
        }
    )
