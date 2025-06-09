from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from assistants.models import Assistant
from assistants.helpers.memory_helpers import create_memory_from_chat
from memory.models import MemoryEntry
from assistants.helpers.logging_helper import log_trail_marker


def generate_assistant_from_demo(demo_slug: str, user, transcript=None):
    """Clone a demo assistant for a user.

    Parameters
    ----------
    demo_slug : str
        slug of the demo assistant
    user : User
        owner of the new assistant
    transcript : list[dict]
        chat messages in the form {"role": "user"|"assistant", "content": str}

    Returns
    -------
    Assistant
    """
    demo = get_object_or_404(Assistant, demo_slug=demo_slug, is_demo=True)

    slug_base = slugify(f"{user.username}-{demo_slug}")
    slug = slug_base
    idx = 1
    while Assistant.objects.filter(slug=slug).exists():
        slug = f"{slug_base}-{idx}"
        idx += 1

    assistant = Assistant.objects.create(
        name=demo.name,
        slug=slug,
        description=demo.description,
        specialty=demo.specialty,
        avatar=demo.avatar,
        avatar_style=demo.avatar_style,
        tone=demo.tone,
        tone_profile=demo.tone_profile,
        personality=demo.personality,
        system_prompt=demo.system_prompt,
        preferred_model=demo.preferred_model,
        primary_badge=demo.primary_badge,
        created_by=user,
        spawn_reason=f"demo:{demo_slug}",
        spawned_by=demo,
        spawned_traits=["badge", "tone", "avatar"],
        is_demo_clone=True,
        is_demo=False,
    )

    # mark conversion from demo
    from assistants.helpers.logging_helper import log_trail_marker

    log_trail_marker(assistant, "demo_converted")

    if transcript:
        pairs = []
        current = []
        for msg in transcript[:6]:
            role = msg.get("role")
            content = msg.get("content", "")
            if role not in {"user", "assistant"}:
                continue
            current.append({"role": role, "content": content})
            if role == "assistant":
                pairs.append(current)
                current = []
        if current:
            pairs.append(current)
        for pair in pairs[:3]:
            user_msgs = [m for m in pair if m["role"] == "user"]
            reply = next((m["content"] for m in pair if m["role"] == "assistant"), "")
            if user_msgs or reply:
                create_memory_from_chat(
                    assistant_name=assistant.name,
                    session_id="demo-transfer",
                    messages=user_msgs,
                    reply=reply,
                    assistant=assistant,
                    is_demo=False,
                )
    if not assistant.memories.exists():
        from assistants.utils.starter_chat import seed_chat_starter_memory

        seed_chat_starter_memory(assistant)
    return assistant


def generate_demo_prompt_preview(demo_assistant) -> str:
    """Return a short system prompt preview for a demo assistant."""
    if demo_assistant.specialty:
        return f"You’re a creative, helpful assistant focused on {demo_assistant.specialty}."
    return "You’re a creative, helpful assistant ready to help the user."


def boost_prompt_from_demo(
    assistant: Assistant, transcript: list[dict] | None = None
) -> str:
    """Generate a short boost summary from demo chat messages."""

    messages = []
    if transcript:
        messages = [
            m.get("content", "") for m in transcript if m.get("role") != "system"
        ]

    demo = (
        assistant.spawned_by
        if assistant.spawned_by and assistant.spawned_by.is_demo
        else None
    )
    if demo:
        starters = MemoryEntry.objects.filter(assistant=demo).order_by("timestamp")[:3]
        for m in starters:
            messages.append(m.summary or m.event)

    if not messages:
        summary = "Based on the demo chat, the assistant showcased its default skills."
    else:
        joined = " ".join(messages)[:500]
        summary = f"This assistant demonstrated: {joined}".strip()

    assistant.prompt_notes = (assistant.prompt_notes or "") + "\n" + summary
    assistant.boosted_from_demo = True
    assistant.save(update_fields=["prompt_notes", "boosted_from_demo"])

    MemoryEntry.objects.create(
        assistant=assistant,
        context=assistant.memory_context,
        event="Demo prompt boost",
        summary=summary,
        type="system_note",
        source_role="system",
    )
    return summary


def preview_boost_summary(demo: Assistant, transcript: list[dict] | None = None) -> str:
    """Return the boost summary without saving anything."""

    messages = []
    if transcript:
        messages += [
            m.get("content", "") for m in transcript if m.get("role") != "system"
        ]
    starters = (
        MemoryEntry.objects.filter(assistant=demo).order_by("timestamp")[:3]
        if demo
        else []
    )
    for m in starters:
        messages.append(m.summary or m.event)

    if not messages:
        return "Based on the demo chat, the assistant showcased its default skills."

    joined = " ".join(messages)[:500]
    return f"This assistant demonstrated: {joined}".strip()


def get_origin_traits(demo: Assistant) -> list[str]:
    """Return badges, tone, or glossary traits cloned from the demo."""

    traits: list[str] = []
    if demo.primary_badge:
        traits.append(demo.primary_badge)
    if demo.tone:
        traits.append(demo.tone)

    entry = (
        MemoryEntry.objects.filter(assistant=demo, anchor__isnull=False)
        .select_related("anchor")
        .order_by("created_at")
        .first()
    )
    if entry and entry.anchor:
        traits.append(entry.anchor.label)

    return traits


def log_demo_reflection(assistant: Assistant, session_id: str) -> None:
    """Save a lightweight reflection for a demo chat."""
    if not assistant.is_demo:
        return
    from assistants.utils.session_utils import load_session_messages
    from assistants.models.reflection import AssistantReflectionLog

    history = load_session_messages(session_id)[:5]
    lines = [
        f"{m['role'].capitalize()}: {m['content']}" for m in history if m.get('role') in {'user', 'assistant'}
    ]
    summary = "\n".join(lines)
    AssistantReflectionLog.objects.create(
        assistant=assistant,
        title="Demo Chat Reflection",
        summary=summary,
        category="meta",
        demo_reflection=True,
    )


def compose_demo_reflection(assistant: Assistant, session_id: str) -> dict:
    """Return a short reflection summary from replay frames."""
    from assistants.utils.session_utils import load_session_messages
    from assistants.utils.chunk_retriever import get_rag_chunk_debug

    messages = load_session_messages(session_id)
    user_msgs = [m.get("content", "") for m in messages if m.get("role") == "user"][:4]
    anchors: set[str] = set()
    fallback = 0
    for text in user_msgs:
        info = get_rag_chunk_debug(str(assistant.id), text)
        anchors.update(
            c.get("anchor_slug")
            for c in info.get("matched_chunks", [])
            if c.get("anchor_slug")
        )
        if info.get("fallback_triggered"):
            fallback += 1

    personality = assistant.tone or assistant.primary_badge or "default style"
    grounded = len(user_msgs) - fallback
    summary = (
        f"During this demo, the assistant replied in {personality}. "
        f"It grounded correctly on {grounded} out of {len(user_msgs)} queries."
    )
    if anchors:
        summary += " Key terms included: " + ", ".join(sorted(anchors)) + "."

    return {"summary": summary, "anchors_used": sorted(anchors), "fallback_count": fallback}
