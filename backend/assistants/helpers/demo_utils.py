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
    return assistant


def generate_demo_prompt_preview(demo_assistant) -> str:
    """Return a short system prompt preview for a demo assistant."""
    if demo_assistant.specialty:
        return (
            f"You’re a creative, helpful assistant focused on {demo_assistant.specialty}."
        )
    return "You’re a creative, helpful assistant ready to help the user."

