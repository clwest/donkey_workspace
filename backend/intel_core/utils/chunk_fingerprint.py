import hashlib
import re


def fingerprint_text(text: str) -> str:
    """Return a stable SHA-256 fingerprint of normalized text."""
    if not text:
        return ""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8", errors="ignore")).hexdigest()
