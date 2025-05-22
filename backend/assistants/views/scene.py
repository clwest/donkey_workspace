from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import uuid

from assistants.models import Assistant, AssistantThoughtLog
from assistants.helpers.chat_helper import get_or_create_chat_session, save_chat_message
from assistants.utils.session_utils import (
    load_session_messages,
    save_message_to_session,
)
from assistants.helpers.memory_helpers import create_memory_from_chat
from memory.utils.replay import replay_scene
from memory.serializers import MemoryEntrySlimSerializer
from mcp_core.models import NarrativeThread
from utils.llm_router import call_llm


@api_view(["GET"])
@permission_classes([AllowAny])
def replay_scene_view(request, slug, thread_id):
    assistant = get_object_or_404(Assistant, slug=slug)
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    block, memories = replay_scene(thread.id, assistant)
    serialized = MemoryEntrySlimSerializer(memories, many=True).data
    return Response({"injection": block, "memories": serialized})


@api_view(["POST"])
@permission_classes([AllowAny])
def chat_with_scene(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    thread_id = request.data.get("thread_id")
    message = request.data.get("message")
    session_id = request.data.get("session_id") or str(uuid.uuid4())
    if not message or not thread_id:
        return Response({"error": "thread_id and message required"}, status=400)
    thread = get_object_or_404(NarrativeThread, id=thread_id)

    injection, memories = replay_scene(thread.id, assistant)

    system_prompt = (
        assistant.system_prompt.content
        if assistant.system_prompt
        else "You are a helpful assistant."
    )
    identity = assistant.get_identity_prompt()
    if identity:
        system_prompt += f"\n\n{identity}"
    system_prompt += f"\n\n{injection}"

    messages = [{"role": "system", "content": system_prompt}]
    messages += load_session_messages(session_id)
    messages.append({"role": "user", "content": message})

    save_message_to_session(session_id, "user", message)
    chat_session = get_or_create_chat_session(
        session_id, assistant=assistant, thread=thread
    )

    try:
        reply = call_llm(messages, model=assistant.preferred_model or "gpt-4o")
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    save_message_to_session(session_id, "assistant", reply)
    save_chat_message(chat_session, "user", message)
    save_chat_message(chat_session, "assistant", reply)

    memory = create_memory_from_chat(
        assistant_name=assistant.name,
        session_id=session_id,
        messages=messages,
        reply=reply,
        chat_session=chat_session,
        assistant=assistant,
        project=chat_session.project,
        narrative_thread=thread,
        thread=thread,
    )

    AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=reply,
        thought_type="generated",
        linked_memory=memory,
        narrative_thread=thread,
        replayed_thread=thread,
    )

    return Response({"reply": reply, "session_id": session_id})
