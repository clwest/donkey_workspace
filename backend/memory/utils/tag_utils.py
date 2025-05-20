from django.utils.text import slugify

MOOD_TAGS = {
    "curious",
    "thoughtful",
    "playful",
    "urgent",
    "focused",
    "confident",
    "optimistic",
    "anxious",
    "frustrated",
    "calm",
    "neutral",
}


def normalize_tag_name(name: str) -> tuple[str, str]:
    """Return normalized (name, slug) pair with mood prefix when applicable."""
    if not name:
        return "", ""
    base = str(name).strip().lower()
    if ":" not in base and base in MOOD_TAGS:
        base = f"mood:{base}"
    return base, slugify(base)
