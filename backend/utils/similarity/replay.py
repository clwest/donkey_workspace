from difflib import SequenceMatcher

def score_drift(original: str, replayed: str) -> float:
    """Return drift score between two texts as 1 - similarity ratio."""
    original = original or ""
    replayed = replayed or ""
    ratio = SequenceMatcher(None, original, replayed).ratio()
    return 1 - ratio
