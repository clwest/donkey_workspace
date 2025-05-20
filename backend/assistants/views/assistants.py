from rest_framework.decorators import api_view, permission_classes
import uuid
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import get_object_or_404
from openai import OpenAI
from datetime import datetime
import logging
import json
from django.conf import settings
from project.models import Project
from mcp_core.models import NarrativeThread
from assistants.helpers.logging_helper import log_assistant_thought
from assistants.models import (
    Assistant,
    AssistantThoughtLog,
    TokenUsage,
    ChatSession,
)
from assistants.helpers.redis_helpers import get_cached_thoughts
from assistants.serializers import AssistantSerializer
from assistants.utils.assistant_session import (
    save_message_to_session,
    flush_session_to_db,
    load_session_messages,
)
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine

from assistants.helpers.chat_helper import get_or_create_chat_session, save_chat_message
from assistants.utils.delegation import spawn_delegated_assistant, should_delegate
from assistants.helpers.memory_helpers import create_memory_from_chat
from memory.models import MemoryEntry
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from memory.utils.context_helpers import get_or_create_context_from_memory
from embeddings.helpers.helpers_io import save_embedding
from embeddings.helpers.helper_tagging import generate_tags_for_memory
from prompts.models import Prompt


logger = logging.getLogger("django")
client = OpenAI()


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistants_view(request):
    """
    Handles listing and creating Assistants.
    GET: Returns all assistants.
    POST: Creates a new assistant with validated data.
    """
    if request.method == "GET":
        assistants = Assistant.objects.all()
        order = request.GET.get("order")
        if order == "msi":
            assistants = assistants.order_by("-mood_stability_index")
        min_msi = request.GET.get("min_msi")
        if min_msi is not None:
            try:
                assistants = assistants.filter(mood_stability_index__gte=float(min_msi))
            except ValueError:
                pass
        serializer = AssistantSerializer(assistants, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        print("🔍 Incoming assistant data:", request.data)
        serializer = AssistantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("❌ Assistant creation failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_detail_view(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response(
            {"error": "Assistant not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = AssistantSerializer(assistant)
    data = serializer.data
    if assistant.current_project:
        from assistants.serializers import ProjectOverviewSerializer

        data["current_project"] = ProjectOverviewSerializer(
            assistant.current_project
        ).data
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def primary_assistant_view(request):
    assistant = Assistant.objects.filter(is_primary=True).first()
    if not assistant:
        return Response({"error": "No primary assistant."}, status=404)

    serializer = AssistantSerializer(assistant)
    recent = get_cached_thoughts(assistant.slug) or []
    data = serializer.data
    data["recent_thoughts"] = recent
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def primary_reflect_now(request):
    """Trigger immediate reflection for the primary assistant."""
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


@api_view(["POST"])
@permission_classes([AllowAny])
def primary_spawn_agent(request):
    """Spawn a delegated assistant from memory using the primary assistant."""
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


@api_view(["POST"])
@permission_classes([AllowAny])
def create_assistant_from_thought(request):
    data = request.data
    required = [
        "name",
        "description",
        "specialty",
        "prompt_id",
        "created_by",
        "project_id",
        # thread_id optional
    ]
    for field in required:
        if field not in data:
            return Response({"error": f"{field} is required"}, status=400)

    prompt = Prompt.objects.get(id=data["prompt_id"])
    creator = get_user_model().objects.get(id=data["created_by"])

    new_assistant = Assistant.objects.create(
        name=data["name"],
        description=data["description"],
        specialty=data["specialty"],
        system_prompt=prompt,
        created_by=creator,
        preferred_model="gpt-4o",
        parent_assistant=parent_assistant,
    )

    AssistantThoughtLog.objects.create(
        assistant_id=data["created_by"],
        project_id=data["project_id"],
        thought_type="planning",
        thought=f"I created a new assistant: {new_assistant.name}, focused on {new_assistant.specialty}.",
        narrative_thread=thread,
    )

    # Bootstrap project & chat session inheriting the thread
    child_project = Project.objects.create(
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
    token_usage, _ = TokenUsage.objects.get_or_create(
        session=chat_session,
        defaults={
            "assistant": assistant,
            "user": user,
            "project": chat_session.project,
            "usage_type": "chat",
        },
    )

    if should_delegate(assistant, token_usage, request.data.get("feedback_flag")):
        recent_memory = (
            MemoryEntry.objects.filter(chat_session=chat_session)
            .order_by("-created_at")
            .first()
        )
        delegate = spawn_delegated_assistant(chat_session, memory_entry=recent_memory)
        return Response({"delegate_slug": delegate.slug})

    # Run OpenAI completion
    completion = client.chat.completions.create(
        model=assistant.preferred_model or "gpt-4o",
        messages=messages,
        temperature=0.7,
    )
    reply = completion.choices[0].message.content.strip()

    usage = completion.usage
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
    engine.log_thought(reply, role="assistant")

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
            model="text-embedding-3-small",
            input=full_transcript,
        )
        embedding_vector = embed_resp.data[0].embedding
        save_embedding(memory, embedding_vector)

        memory.tags = generate_tags_for_memory(full_transcript)
        memory.save()

    return Response({"messages": load_session_messages(session_id)})


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
def self_reflect(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    engine = AssistantReflectionEngine(assistant)
    prompt = f"You are {assistant.name}. Reflect on your recent behavior and suggest updates to your persona_summary, traits, values or motto. Respond with reflection text followed by JSON updates if any."
    output = engine.generate_reflection(prompt)
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
        if updates.get("values") is not None:
            assistant.values = updates["values"]
        if updates.get("motto"):
            assistant.motto = updates["motto"]
        assistant.save()

    return Response({"summary": text, "updates": updates})


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
        project = Project.objects.get(id=project_id)
        creator = assistant.created_by
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found."}, status=404)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=404)

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
