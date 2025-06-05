from typing import Dict, List
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from assistants.utils.chunk_retriever import get_rag_chunk_debug
from utils.rag_debug import log_rag_debug


def run_assistant_rag_test(
    assistant: Assistant, *, disable_scope: bool = False
) -> Dict[str, object]:
    """Simulate RAG retrieval for all glossary anchors."""
    anchors = SymbolicMemoryAnchor.objects.all().order_by("slug")
    issues: List[str] = []
    for anchor in anchors:
        debug_info = get_rag_chunk_debug(
            str(assistant.id),
            anchor.label,
            disable_scope=disable_scope,
        )
        used = debug_info["matched_chunks"] + debug_info["fallback_chunks"]
        hit = any(
            anchor.slug == c.get("anchor_slug")
            or anchor.slug in c.get("matched_anchors", [])
            for c in used
        )
        log_rag_debug(
            assistant,
            anchor.label,
            {
                "used_chunks": used,
                "rag_fallback": debug_info["fallback_triggered"],
                "fallback_reason": debug_info.get("reason"),
                "anchor_hits": [anchor.slug] if hit else [],
                "anchor_misses": [] if hit else [anchor.slug],
                "retrieval_score": debug_info["retrieval_score"],
                "fallback_chunk_scores": [
                    debug_info["scores"][c["chunk_id"]] for c in used
                ],
            },
            debug=True,
            expected_anchor=anchor.slug,
        )
        if not hit:
            issues.append(anchor.slug)
    return {"passed": len(issues) == 0, "issues": issues}


def run_rag_diagnostics(*, disable_scope: bool = False) -> List[Dict[str, object]]:
    """Run RAG tests for all assistants."""
    results = []
    for a in Assistant.objects.all():
        res = run_assistant_rag_test(a, disable_scope=disable_scope)
        results.append({"assistant": a.slug, **res})
    return results
