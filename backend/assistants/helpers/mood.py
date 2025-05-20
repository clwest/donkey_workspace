"""Simple heuristics for mood detection from text."""

import re


MOOD_KEYWORDS = {
    "anxious": ["worried", "anxious", "nervous", "concerned"],
    "frustrated": ["frustrated", "angry", "upset", "annoyed"],
    "optimistic": ["optimistic", "hopeful", "excited", "happy"],
    "confident": ["confident", "sure", "certain"],
}

# Preferred tone mapping for each mood
MOOD_TO_TONE = {
    "curious": "encouraging",
    "frustrated": "direct",
    "playful": "playful",
    "urgent": "urgent",
    "reflective": "empathetic",
}


def detect_mood(text: str) -> str:
    """Return a short mood label based on keywords in ``text``."""
    if not text:
        return "neutral"

    lowered = text.lower()
    for mood, words in MOOD_KEYWORDS.items():
        pattern = r"|".join(re.escape(w) for w in words)
        if re.search(pattern, lowered):
            return mood

    return "neutral"


def map_mood_to_tone(mood: str) -> str:
    """Return the default tone for a mood."""
    return MOOD_TO_TONE.get(mood, "neutral")


def get_session_mood(session) -> str:
    """Return the stored mood for a chat session if available."""
    if not session:
        return "neutral"
    memory = (
        session.structured_memories.filter(memory_key="mood")
        .order_by("-created_at")
        .first()
    )
    if memory:
        return memory.memory_value
    return "neutral"
