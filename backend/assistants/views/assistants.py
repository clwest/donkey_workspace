from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import viewsets
import uuid
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import get_object_or_404
from openai import OpenAI
from utils.llm_router import call_llm
from prompts.utils.token_helpers import EMBEDDING_MODEL
import utils.llm_router as llm_router
from datetime import datetime
import logging
import json
import re
from django.conf import settings
from django.utils.text import slugify
from assistants.services import AssistantService
from memory.services import MemoryService
from assistants.helpers.logging_helper import log_assistant_thought
from assistants.models.assistant import (
    Assistant,
    TokenUsage,
    ChatSession,
    AssistantMessage,
    AssistantSkill,
)
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.thoughts import AssistantThoughtLog
from prompts.models import PromptMutationLog
from assistants.utils.session_utils import get_cached_thoughts
from assistants.serializers import AssistantSerializer
from assistants.utils.session_utils import (
    save_message_to_session,
    flush_session_to_db,
    load_session_messages,
)
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
from assistants.helpers.deletion import cascade_delete_assistant

from assistants.helpers.chat_helper import get_or_create_chat_session, save_chat_message
from assistants.utils.delegation import spawn_delegated_assistant, should_delegate
from assistants.helpers.memory_helpers import create_memory_from_chat
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from memory.utils.context_helpers import get_or_create_context_from_memory
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
    permission_classes = [AllowAny]
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
        old_name = assistant.name

        new_name = request.data.get("name")
        new_slug = request.data.get("slug")
        description = request.data.get("description")
        tone = request.data.get("tone")
        preferred_model = request.data.get("preferred_model")
        system_prompt_id = request.data.get("system_prompt")

        if new_slug and Assistant.objects.filter(slug=new_slug).exclude(id=assistant.id).exists():
            return Response({"error": "Slug already exists"}, status=400)

        if new_name is not None:
            assistant.name = new_name
            if not new_slug:
                base_slug = slugify(new_name)
                unique_slug = base_slug
                i = 1
                while Assistant.objects.filter(slug=unique_slug).exclude(id=assistant.id).exists():
                    unique_slug = f"{base_slug}-{i}"
                    i += 1
                new_slug = unique_slug

        if new_slug:
            assistant.slug = new_slug

        if description is not None:
            assistant.description = description

        if tone is not None:
            assistant.tone = tone

        if preferred_model is not None:
            assistant.preferred_model = preferred_model

        if system_prompt_id is not None:
            try:
                prompt_obj = Prompt.objects.get(id=system_prompt_id)
            except (ValueError, Prompt.DoesNotExist):
                return Response({"error": "Invalid system_prompt"}, status=400)
            assistant.system_prompt = prompt_obj

        assistant.save()

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

        qp = request.query_params
        force = qp.get("force") == "true" or request.data.get("force")
        cascade = qp.get("cascade") == "true" or request.data.get("cascade")
        if cascade:
            force = True

        from project.models import Project
        from assistants.models.assistant import ChatSession
        from memory.models import MemoryEntry

        has_live_projects = Project.objects.filter(assistant=assistant, status="active").exists()
        has_children = assistant.sub_assistants.exists()
        if (has_live_projects or has_children) and not force:
            return Response({"error": "Assistant in use", "hint": "Pass force=true or cascade=true"}, status=400)

        if cascade:
            cascade_delete_assistant(assistant)
            logger.info("Assistant %s and children deleted", slug)
            return Response(status=204)

        ChatSession.objects.filter(assistant=assistant).delete()
        Project.objects.filter(assistant=assistant).delete()
        MemoryEntry.objects.filter(assistant=assistant).update(assistant=None)
        MemoryEntry.objects.filter(chat_session__assistant=assistant).update(chat_session=None)

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
        parent = Assistant.objects.filter(is_primary=True).first()
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
            .annotate(has_sessions=models.Exists(ChatSession.objects.filter(assistant=models.OuterRef("pk"))) )
            .annotate(project_count=models.Count("project"))
        )
        unused = qs.filter(has_sessions=False, project_count=0)
        count = unused.count()
        unused.delete()
        logger.info("cleanup_unused deleted %s assistants", count)
        return Response({"deleted": count})


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistants_view(request):
    warnings.warn(
        "assistants_view is deprecated; use AssistantViewSet instead",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view({"get": "list", "post": "create"})
    return view(request)


@api_view(["GET"])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def primary_assistant_view(request):
    warnings.warn(
        "primary_assistant_view is deprecated; use AssistantViewSet.primary",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view({"get": "primary"})
    return view(request)


@api_view(["POST"])
@permission_classes([AllowAny])
def primary_reflect_now(request):
    """Trigger immediate reflection for the primary assistant."""
    warnings.warn(
        "primary_reflect_now is deprecated; use AssistantViewSet.primary_reflect_now",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view({"post": "primary_reflect_now"})
    return view(request)


@api_view(["POST"])
@permission_classes([AllowAny])
def primary_spawn_agent(request):
    """Spawn a delegated assistant from memory using the primary assistant."""
    warnings.warn(
        "primary_spawn_agent is deprecated; use AssistantViewSet.primary_spawn_agent",
        DeprecationWarning,
    )
    view = AssistantViewSet.as_view({"post": "primary_spawn_agent"})
    return view(request)


@api_view(["POST"])
@permission_classes([AllowAny])
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
            spawned_by="manual",
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
@permission_classes([AllowAny])
def assistant_from_documents(request):
    """Create an assistant from one or more Documents."""
    data = request.data
    doc_ids = data.get("document_ids") or []
    if not isinstance(doc_ids, list) or len(doc_ids) == 0:
        return Response({"error": "document_ids required"}, status=400)

    documents = list(Document.objects.filter(id__in=doc_ids))
    if not documents:
        return Response({"error": "Documents not found"}, status=404)

    doc_set = DocumentSet.objects.create(
        title=f"Ad Hoc Set: {datetime.now().date()}"
    )
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
            spawned_by="manual",
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


@api_view(["POST"])
@permission_classes([AllowAny])
def chat_with_assistant_view(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    user = request.user if request.user.is_authenticated else None

    message = request.data.get("message")
    session_id = request.data.get("session_id") or str(uuid.uuid4())

    if message == "__ping__":
        return Response({"messages": load_session_messages(session_id)})

    if not message:
        return Response({"error": "Empty message."}, status=status.HTTP_400_BAD_REQUEST)

    # Build messages list
    system_prompt = (
        assistant.system_prompt.content
        if assistant.system_prompt
        else "You are a helpful assistant."
    )
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
    reply, summoned_ids, rag_meta = llm_router.chat(
        messages,
        assistant,
        temperature=0.7,
        auto_expand=not request.data.get("focus_only", True),
        focus_anchors_only=request.data.get("focus_only", True),
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
    AssistantThoughtLog.objects.create(
        assistant=assistant,
        project=None,
        thought="Manually testing role override",
        role="user",
        thought_trace="manual",
    )

    # Save chat log
    user_chat = save_chat_message(chat_session, "user", message)
    assistant_chat = save_chat_message(chat_session, "assistant", reply)
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
    )

    if rag_meta.get("convergence_log_id"):
        from memory.models import AnchorConvergenceLog

        AnchorConvergenceLog.objects.filter(id=rag_meta["convergence_log_id"]).update(memory=memory)

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

        memory.tags = generate_tags_for_memory(full_transcript)
        memory.save()

    return Response(
        {
            "messages": load_session_messages(session_id),
            "rag_meta": rag_meta,
        }
    )


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
@permission_classes([AllowAny])
def demo_assistant(request):
    assistant = Assistant.objects.filter(is_demo=True)
    data = [
        {
            "name": a.name,
            "slug": a.slug,
            "description": a.description,
            "avatar": a.avatar,
        }
        for a in assistant
    ]
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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
def recover_assistant_view(request, slug):
    """Generate a recovery summary and prompt revision for the assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from assistants.utils.recovery import (
        create_prompt_revision,
        generate_recovery_summary,
    )

    summary = generate_recovery_summary(assistant)
    create_prompt_revision(assistant)

    assistant.needs_recovery = False
    assistant.save(update_fields=["needs_recovery"])

    AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=f"Recovery run: {summary}",
        thought_type="reflection",
        category="meta",
    )

    return Response({"summary": summary})


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
