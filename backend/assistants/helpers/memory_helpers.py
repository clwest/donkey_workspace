import json
import logging
from openai import OpenAI
from django.utils.text import slugify
from mcp_core.models import Tag
from memory.models import MemoryEntry
from assistants.tasks import embed_and_tag_memory, run_assistant_reflection
from embeddings.helpers.helpers_io import save_embedding


client = OpenAI()
logger = logging.getLogger(__name__)


import re


def create_memory_from_chat(
    assistant_name,
    session_id,
    messages,
    reply,
    *,
    chat_session=None,
    assistant=None,
    project=None,
    importance=5,
    narrative_thread=None,
):
    transcript = "\n".join(
        [
            f"{m['role'].capitalize()}: {m['content'].strip()}"
            for m in messages
            if m["role"] in ("user", "assistant")
        ]
        + [f"Assistant: {reply}"]
    )

    if not narrative_thread and chat_session:
        narrative_thread = chat_session.thread or chat_session.narrative_thread
    if not narrative_thread and project:
        narrative_thread = project.thread or project.narrative_thread

    identity = assistant.get_identity_prompt() if assistant else ""
    event_text = f"Conversation with assistant {assistant_name}"
    if identity:
        event_text += f" | {identity}"
    memory = MemoryEntry.objects.create(
        event=event_text,
        emotion="neutral",
        importance=importance,
        is_conversation=True,
        session_id=session_id,
        full_transcript=transcript,
        chat_session=chat_session,
        assistant=assistant,
        related_project=project,
        narrative_thread=narrative_thread,
    )

    embed_and_tag_memory.delay(memory.id)
    run_assistant_reflection.delay(memory.id)
    return memory
