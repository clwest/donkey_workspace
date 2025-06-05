from datetime import timedelta
from django.utils import timezone
from memory.models import (
    RAGGroundingLog,
    GlossaryChangeEvent,
    SymbolicMemoryAnchor,
)
from intel_core.models import DocumentChunk
from django.utils.text import slugify

def log_rag_debug(assistant, query, rag_meta, debug=False, expected_anchor=None):
    """Persist RAG debug info, always logging when fallback occurs."""
    if not debug and not rag_meta.get("rag_fallback", False):
        return None
    used_ids = [c.get("chunk_id") for c in rag_meta.get("used_chunks", [])]
    corrected = rag_meta.get("retrieval_score", 0.0)
    if rag_meta.get("rag_fallback") and rag_meta.get("fallback_chunk_scores"):
        corrected = max(rag_meta.get("fallback_chunk_scores"))
    try:
        return RAGGroundingLog.objects.create(
            assistant=assistant,
            query=query,
            used_chunk_ids=used_ids,
            fallback_triggered=rag_meta.get("rag_fallback", False),
            fallback_reason=rag_meta.get("fallback_reason"),
            expected_anchor=expected_anchor or "",
            glossary_hits=rag_meta.get("anchor_hits", []),
            glossary_misses=rag_meta.get("anchor_misses", []),
            retrieval_score=rag_meta.get("retrieval_score", 0.0),
            corrected_score=corrected,
            raw_score=rag_meta.get("raw_score"),
            adjusted_score=rag_meta.get("adjusted_score"),
            glossary_boost_applied=rag_meta.get("glossary_boost_applied", 0.0),
            boosted_from_reflection=rag_meta.get("boosted_from_reflection", False),
            reflection_boost_score=rag_meta.get("reflection_boost_score", 0.0),
            glossary_boost_type=rag_meta.get("glossary_boost_type", ""),
            fallback_threshold_used=rag_meta.get("fallback_threshold_used"),
        )
    except Exception as e:  # pragma: no cover - failsafe for missing fields
        if "expected_anchor" in str(e):
            return RAGGroundingLog.objects.create(
                assistant=assistant,
                query=query,
                used_chunk_ids=used_ids,
                fallback_triggered=rag_meta.get("rag_fallback", False),
                fallback_reason=rag_meta.get("fallback_reason"),
                glossary_hits=rag_meta.get("anchor_hits", []),
                glossary_misses=rag_meta.get("anchor_misses", []),
                retrieval_score=rag_meta.get("retrieval_score", 0.0),
                corrected_score=corrected,
                raw_score=rag_meta.get("raw_score"),
                adjusted_score=rag_meta.get("adjusted_score"),
                glossary_boost_applied=rag_meta.get("glossary_boost_applied", 0.0),
                boosted_from_reflection=rag_meta.get("boosted_from_reflection", False),
                reflection_boost_score=rag_meta.get("reflection_boost_score", 0.0),
                glossary_boost_type=rag_meta.get("glossary_boost_type", ""),
                fallback_threshold_used=rag_meta.get("fallback_threshold_used"),
            )
        raise

def get_recent_logs(assistant, hours=24):
    start = timezone.now() - timedelta(hours=hours)
    return RAGGroundingLog.objects.filter(
        assistant=assistant, created_at__gte=start
    ).order_by("-created_at")

def boost_glossary_anchor(term, boost=0.1):
    slug = slugify(term)
    anchor, _ = SymbolicMemoryAnchor.objects.get_or_create(slug=slug, defaults={"label": term})
    updated = DocumentChunk.objects.filter(anchor=anchor).update(glossary_boost=boost)
    GlossaryChangeEvent.objects.create(term=term, boost=boost)
    return updated
