from assistants.models.assistant import Assistant
from assistants.models.trail import TrailMarkerLog
from memory.models import MemoryEntry

TONE_COLORS = {
    "cheerful": {"bg": "#fff7e6", "fg": "#d9480f"},
    "formal": {"bg": "#e7f1ff", "fg": "#1c64f2"},
    "nerdy": {"bg": "#f3e8ff", "fg": "#6f42c1"},
    "zen": {"bg": "#e6fffa", "fg": "#0f5132"},
    "friendly": {"bg": "#e6fffb", "fg": "#0d9488"},
    "mysterious": {"bg": "#f8f9fa", "fg": "#6c757d"},
}


def get_intro_splash_payload(assistant: Assistant) -> dict:
    """Return intro splash data for the assistant."""
    colors = TONE_COLORS.get(assistant.tone_profile or "", {})
    flair = None
    if assistant.primary_badge:
        from assistants.models.badge import Badge

        badge = Badge.objects.filter(slug=assistant.primary_badge).first()
        flair = badge.emoji if badge else None
    elif assistant.spawned_by and assistant.spawned_by.primary_badge:
        from assistants.models.badge import Badge

        badge = Badge.objects.filter(slug=assistant.spawned_by.primary_badge).first()
        flair = badge.emoji if badge else None
    badges = assistant.skill_badges or []
    if not badges and assistant.spawned_by and assistant.spawned_by.skill_badges:
        badges = assistant.spawned_by.skill_badges
    summary_entry = (
        MemoryEntry.objects.filter(assistant=assistant, type="milestone_summary")
        .order_by("-created_at")
        .first()
    )
    milestones = list(
        assistant.trail_markers.order_by("-timestamp")
        .values("marker_type", "timestamp", "notes")[:3]
    )
    return {
        "name": assistant.name,
        "avatar_url": assistant.avatar,
        "archetype": assistant.archetype,
        "badges": badges,
        "intro_text": assistant.intro_text or "",
        "archetype_summary": assistant.archetype_summary or "",
        "flair": flair,
        "theme_colors": colors,
        "demo_origin": assistant.spawned_by.name if assistant.spawned_by and assistant.spawned_by.is_demo else None,
        "preview_traits": {
            "badge": assistant.primary_badge or getattr(assistant.spawned_by, "primary_badge", None),
            "tone": assistant.tone_profile or assistant.tone or getattr(assistant.spawned_by, "tone_profile", None),
            "avatar": assistant.avatar_style or getattr(assistant.spawned_by, "avatar_style", None),
        },
        "trail_summary": summary_entry.summary if summary_entry else None,
        "recent_milestones": milestones,
    }


def get_personalization_prompt(assistant: Assistant) -> dict:
    """Return rename and trait suggestions for a cloned assistant."""
    demo = assistant.spawned_by if assistant.spawned_by and assistant.spawned_by.is_demo else None
    if not demo:
        return {}

    base = demo.name
    suggestions = [f"My {base}", f"{base} Pro", f"{base} Plus"]

    description = demo.personality_description or demo.specialty or ""

    return {
        "suggested_names": suggestions,
        "traits": {
            "tone": assistant.tone or demo.tone,
            "badge": assistant.primary_badge or demo.primary_badge,
            "avatar": assistant.avatar or "",
        },
        "inherit_description": description,
    }
