"""Simple heuristics for mood detection from text."""

import re


MOOD_KEYWORDS = {
    "anxious": ["worried", "anxious", "nervous", "concerned"],
    "frustrated": ["frustrated", "angry", "upset", "annoyed"],
    "optimistic": ["optimistic", "hopeful", "excited", "happy"],
    "confident": ["confident", "sure", "certain"],
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

