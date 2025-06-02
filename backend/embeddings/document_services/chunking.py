"""
chunking.py

Text chunking logic for document embeddings.
"""

import re
import hashlib
from typing import List, Tuple

from intel_core.core.filters import ALL_STOP_WORDS
import spacy

try:
    from nltk.tokenize import sent_tokenize

    _has_nltk = True
except ImportError:
    _has_nltk = False

MAX_SUMMARY_CHARS = 1000

CHUNK_OVERLAP = 0.1  # 10% overlap
MAX_CHUNKS_PER_DOCUMENT = 500

__all__ = [
    "generate_chunks",
    "generate_chunk_fingerprint",
    "fingerprint_similarity",
    "split_text",
    "fingerprint",
    "summarize_chunks",
    "merge_and_score_chunks",
    "clean_and_score_chunk",
]

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:  # pragma: no cover - fallback when model unavailable
    nlp = spacy.blank("en")


def lexical_density(text: str) -> float:
    """Return lexical density (ratio of non-stopwords to total words)."""
    words = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return 0.0
    content = [w for w in words if w not in ALL_STOP_WORDS]
    return len(content) / len(words)


def clean_and_score_chunk(text: str, chunk_index: int | None = None) -> dict:
    """Clean and score a text chunk for relevance."""
    cleaned = text.strip()
    score = 0.0
    if chunk_index in (0, 1):
        return {
            "text": cleaned,
            "score": score,
            "keep": True,
            "origin": "forced",
            "reason": "first_chunks",
        }
    words = cleaned.split()
    if len(words) < 5:
        return {
            "text": cleaned,
            "score": 0.0,
            "keep": False,
            "reason": "too_short",
        }

    if len(words) < 15:
        return {
            "text": cleaned,
            "score": 0.0,
            "keep": False,
            "reason": "short_low_quality",
        }

    non_stop = [w for w in words if w.lower() not in ALL_STOP_WORDS]
    if len(non_stop) / len(words) < 0.5:
        return {
            "text": cleaned,
            "score": 0.0,
            "keep": False,
            "reason": "low_lexical_density",
        }

    if HEADER_FOOTER_RE.search(cleaned):
        return {
            "text": cleaned,
            "score": 0.0,
            "keep": False,
            "reason": "header_footer",
        }

    if not re.search(r"[.!?]", cleaned):
        return {
            "text": cleaned,
            "score": 0.0,
            "keep": False,
            "reason": "no_sentence_punctuation",
        }

    filler_phrases = [
        "hey guys",
        "thanks for watching",
        "subscribe",
        "welcome back",
    ]
    lowered = cleaned.lower()
    if any(p in lowered for p in filler_phrases):
        return {
            "text": cleaned,
            "score": 0.0,
            "keep": False,
            "reason": "filler_phrase",
        }

    keywords = ["setup", "install", "workflow", "step by step", "codex"]
    if any(k in lowered for k in keywords):
        score += 0.4

    doc = nlp(cleaned)
    if any(tok.pos_ == "VERB" for tok in doc):
        score += 0.1
    if doc.ents:
        score += 0.1
    if any(w[0].isupper() for w in words):
        score += 0.05

    if cleaned.endswith(('.', '?', '!')):
        score += 0.3

    keep = score > 0.3
    return {
        "text": cleaned,
        "score": score,
        "keep": keep,
        "reason": "low_score" if not keep else "ok",
    }


def generate_chunks(text: str, chunk_size: int = 1000) -> List[str]:
    """
    Split text into chunks with overlap.
    """
    overlap = int(chunk_size * CHUNK_OVERLAP)
    if not text or chunk_size <= overlap:
        return []
    chunks = []
    text_length = len(text)
    step = chunk_size - overlap
    for start in range(0, text_length, step):
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        if len(chunk) < 50:
            if lexical_density(chunk) < 0.4:
                continue
        chunks.append(chunk)
        if len(chunks) >= MAX_CHUNKS_PER_DOCUMENT:
            break
    return chunks


def generate_chunk_fingerprint(text: str) -> str:
    """
    Generate a fingerprint for deduplicating similar chunks.
    """
    processed = text.lower()
    processed = re.sub(r"[^\w\s]", " ", processed)
    processed = re.sub(r"\s+", " ", processed).strip()
    words = processed.split()
    # Remove common stopwords
    common = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "for",
        "of",
        "in",
        "on",
        "at",
        "to",
        "by",
        "this",
        "that",
        "with",
    }
    filtered = [w for w in words if w not in common]
    sampler = filtered
    if len(filtered) > 150:
        mid = len(filtered) // 2
        sampler = filtered[:50] + filtered[mid - 25 : mid + 25] + filtered[-50:]
    fingerprint_str = " ".join(sampler)
    # Surrogate characters from badly encoded pages can break utf-8 encoding
    # during fingerprint generation. Ignore any invalid code points so the
    # fingerprint function is more robust to noisy text.
    fingerprint_bytes = fingerprint_str.encode("utf-8", errors="ignore")
    return hashlib.md5(fingerprint_bytes).hexdigest()


def fingerprint_similarity(fp1: str, fp2: str) -> float:
    """
    Compute similarity between two hex digest fingerprints.
    """
    if not fp1 or not fp2:
        return 0.0
    matches = sum(c1 == c2 for c1, c2 in zip(fp1, fp2))
    return matches / max(len(fp1), len(fp2))


def split_text(text: str, max_tokens: int = 500) -> List[str]:
    """
    Split text into segments of up to max_tokens approximate tokens (by word count),
    attempting to split at sentence boundaries.
    """
    if not text or max_tokens <= 0:
        return []
    # Sentence segmentation
    if _has_nltk:
        sentences = sent_tokenize(text)
    else:
        sentences = re.split(r"(?<=[\.\!\?])\s+", text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0
    for sentence in sentences:
        words = sentence.split()
        length = len(words)
        if current_len + length <= max_tokens:
            current.append(sentence)
            current_len += length
        else:
            if current:
                chunks.append(" ".join(current))
            if length > max_tokens:
                # split long sentence into word-based chunks
                for i in range(0, length, max_tokens):
                    sub = words[i : i + max_tokens]
                    chunks.append(" ".join(sub))
                current = []
                current_len = 0
            else:
                current = [sentence]
                current_len = length
    if current:
        chunks.append(" ".join(current))
    return chunks


def fingerprint(text: str) -> str:
    """
    Generate a stable SHA-256 fingerprint for deduplication.
    """
    if not text:
        return ""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    fingerprint_bytes = normalized.encode("utf-8", errors="ignore")
    return hashlib.sha256(fingerprint_bytes).hexdigest()


def summarize_chunks(chunks: List[str]) -> str:
    """
    Join chunks into a single summary string, truncated to MAX_SUMMARY_CHARS.
    """
    summary = " ".join(chunk.strip() for chunk in chunks if chunk)
    if len(summary) <= MAX_SUMMARY_CHARS:
        return summary
    truncated = summary[:MAX_SUMMARY_CHARS].rsplit(" ", 1)[0]
    return truncated + "..."


def _token_count(text: str) -> int:
    """Approximate token count using whitespace-separated words."""
    return len(text.split())


HEADER_FOOTER_RE = re.compile(r"page \d+ of \d+", re.IGNORECASE)


def merge_and_score_chunks(
    chunks: List[str],
    small_threshold: int = 100,
    max_total_tokens: int = 300,
) -> List[Tuple[str, float, str]]:
    """Clean up, merge, and score chunks.

    Args:
        chunks: Raw text chunks.
        small_threshold: Token threshold for considering a chunk small.
        max_total_tokens: Max tokens when merging adjacent small chunks.

    Returns:
        List of tuples ``(text, score, notes)``.
    """

    results: List[Tuple[str, float, str]] = []
    seen_fps = set()
    i = 0
    while i < len(chunks):
        text = chunks[i].strip()
        if not text:
            i += 1
            continue

        if HEADER_FOOTER_RE.match(text):
            results.append((text, 0.0, "discarded header/footer"))
            i += 1
            continue

        alnum_ratio = sum(c.isalnum() for c in text) / max(len(text), 1)
        if alnum_ratio < 0.4:
            results.append((text, 0.0, "discarded non-alphanumeric"))
            i += 1
            continue

        fp = fingerprint(text)
        if fp in seen_fps:
            results.append((text, 0.0, "duplicate chunk"))
            i += 1
            continue

        tokens = _token_count(text)
        notes = ""
        if tokens < small_threshold and i + 1 < len(chunks):
            nxt = chunks[i + 1].strip()
            if nxt:
                combined = text + " " + nxt
                if tokens + _token_count(nxt) <= max_total_tokens:
                    text = combined
                    tokens = _token_count(text)
                    notes = "merged with next"
                    i += 1

        score = 0.5 if tokens < small_threshold else 1.0
        results.append((text, score, notes))
        seen_fps.add(fp)
        i += 1

    return results
