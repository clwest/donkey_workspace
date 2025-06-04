from __future__ import annotations

import re
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING
from difflib import SequenceMatcher

from nltk.stem import PorterStemmer

if TYPE_CHECKING:  # Avoid circular import during runtime
    from assistants.models.assistant import Assistant
from intel_core.models import DocumentChunk
from memory.models import SymbolicMemoryAnchor, MemoryEntry

stemmer = PorterStemmer()


def _match_anchor(
    anchor: SymbolicMemoryAnchor, text: str
) -> Tuple[bool, Optional[str]]:
    """Return (True, method) if ``text`` references ``anchor``."""
    if not text:
        return False, None
    text_lower = text.lower()
    tokens = [stemmer.stem(t) for t in re.findall(r"[a-zA-Z0-9']+", text_lower)]
    for term in filter(None, [anchor.slug.replace("-", " "), anchor.label]):
        term_lower = term.lower()
        if term_lower in text_lower:
            return True, "exact"
        stem = stemmer.stem(term_lower)
        if stem in tokens or stem.rstrip("s") in tokens:
            return True, "stem"
        ratio = SequenceMatcher(None, term_lower, text_lower).ratio()
        if ratio >= 0.85:
            return True, "fuzzy"
    return False, None


def retag_glossary_chunks(
    assistant: Assistant,
    *,
    dry_run: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Retag chunks for ``assistant`` and return match info."""
    chunks = DocumentChunk.objects.filter(document__linked_assistants=assistant)
    anchors = SymbolicMemoryAnchor.objects.filter(reinforced_by=assistant)
    results: Dict[str, Dict[str, str]] = {}
    for anchor in anchors:
        info: Dict[str, str] = {}
        for chunk in chunks:
            matched, via = _match_anchor(anchor, chunk.text)
            if not matched:
                continue
            info[str(chunk.id)] = via or "exact"
            if dry_run:
                continue
            changed = False
            if anchor.slug not in chunk.matched_anchors:
                chunk.matched_anchors.append(anchor.slug)
                changed = True
            if not chunk.is_glossary:
                chunk.is_glossary = True
                changed = True
            if changed:
                chunk.save(update_fields=["matched_anchors", "is_glossary"])
        results[anchor.slug] = info
    return results


def retag_memory_glossary_terms(memory: MemoryEntry) -> List[str]:
    """Attach glossary anchors to ``memory`` text fields."""
    text = " ".join(
        t for t in [memory.event, memory.summary, memory.full_transcript] if t
    )
    if not text:
        return []
    anchors = (
        SymbolicMemoryAnchor.objects.filter(reinforced_by=memory.assistant)
        if memory.assistant
        else SymbolicMemoryAnchor.objects.all()
    )
    matched: List[str] = []
    for anchor in anchors:
        found, _ = _match_anchor(anchor, text)
        if not found:
            continue
        matched.append(anchor.slug)
        if memory.anchor_id == anchor.id:
            continue
        if not memory.anchor_id:
            memory.anchor = anchor
    if matched:
        memory.save(update_fields=["anchor"])
    return matched
