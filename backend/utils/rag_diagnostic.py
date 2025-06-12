from typing import Any, Optional
from django.utils import timezone
from assistants.models import Assistant
from mcp_core.models import MemoryContext
from memory.models import RAGDiagnosticLog


def log_rag_diagnostic(
    assistant: Assistant,
    query_text: str,
    rag_meta: dict[str, Any],
    *,
    memory_context_id: Optional[str] = None,
    token_usage: Optional[dict[str, Any]] = None,
) -> RAGDiagnosticLog:
    """Create a RAGDiagnosticLog entry from rag_meta info."""
    context = None
    if memory_context_id:
        context = MemoryContext.objects.filter(id=memory_context_id).first()
    chunks = rag_meta.get("used_chunks") or rag_meta.get("candidates") or []
    if isinstance(chunks, list):
        avg_score = sum(float(c.get("score", c.get("final_score", 0.0))) for c in chunks) / max(len(chunks), 1)
    else:
        avg_score = 0.0
    log = RAGDiagnosticLog.objects.create(
        assistant=assistant,
        query_text=query_text,
        retrieved_chunks=chunks,
        fallback_triggered=rag_meta.get("rag_fallback", False),
        glossary_matches=rag_meta.get("anchor_hits", []),
        used_memory_context=context,
        reflection_boosts_applied=rag_meta.get("reflection_hits", []),
        confidence_score_avg=avg_score,
        token_usage=token_usage,
        explanation_text=rag_meta.get("fallback_reason") or rag_meta.get("rag_ignored_reason") or "",
        timestamp=timezone.now(),
    )
    return log
