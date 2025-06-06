from typing import Dict, List, Optional
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from assistants.utils.chunk_retriever import get_rag_chunk_debug
from utils.rag_debug import log_rag_debug
from tqdm import tqdm
import time


def run_assistant_rag_test(
    assistant: Assistant,
    *,
    limit: Optional[int] = None,
    disable_scope: bool = False,
) -> Dict[str, object]:
    """Simulate RAG retrieval for all glossary anchors."""
    anchors = SymbolicMemoryAnchor.objects.all().order_by("slug")
    if limit:
        anchors = anchors[:limit]

    issues: List[str] = []
    detailed: List[dict] = []
    start = time.time()
    for anchor in tqdm(anchors, desc=f"🔍 Testing glossary for {assistant.slug}"):
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
                    debug_info["scores"].get(c["chunk_id"], 0.0) for c in used
                ],
            },
            debug=True,
            expected_anchor=anchor.slug,
        )
        if not hit:
            issues.append(anchor.slug)
        top_chunk = used[0] if used else None
        final_score = (
            debug_info["scores"].get(top_chunk["chunk_id"], 0.0) if top_chunk else 0.0
        )
        glossary_boost = (
            debug_info["glossary_scores"].get(top_chunk["chunk_id"], 0.0)
            if top_chunk
            else 0.0
        )
        detailed.append(
            {
                "anchor": anchor.label,
                "hits": len(debug_info["matched_chunks"]),
                "fallbacks": len(debug_info["fallback_chunks"]),
                "final_score": final_score,
                "glossary_boost": glossary_boost,
                "status": (
                    "fallback"
                    if debug_info["fallback_triggered"]
                    else ("ok" if hit else "miss")
                ),
            }
        )
    elapsed = time.time() - start
    total = len(anchors)
    pass_rate = (total - len(issues)) / total if total else 0.0
    return {
        "assistant": assistant.slug,
        "tested": total,
        "issues_found": len(issues),
        "pass_rate": pass_rate,
        "duration": elapsed,
        "results": detailed,
    }


def run_rag_diagnostics(
    *, limit: Optional[int] = None, disable_scope: bool = False
) -> List[Dict[str, object]]:
    """Run RAG tests for all assistants."""
    results: List[Dict[str, object]] = []
    for a in Assistant.objects.all():
        res = run_assistant_rag_test(a, limit=limit, disable_scope=disable_scope)
        results.append({"assistant": a.slug, **res})
    return results
