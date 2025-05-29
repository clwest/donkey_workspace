from rest_framework.decorators import api_view
from rest_framework.response import Response
from intel_core.models import DocumentChunk

@api_view(["GET"])
def debug_doc_chunks(request, doc_id):
    chunks = DocumentChunk.objects.filter(document_id=doc_id).order_by("order")
    out = [
        {
            "id": str(c.id),
            "order": c.order,
            "tokens": c.tokens,
            "score": c.score,
            "glossary_score": c.glossary_score,
            "matched_anchors": c.matched_anchors,
            "fingerprint": c.fingerprint,
            "text_preview": c.text[:300],
        }
        for c in chunks
    ]
    return Response(out)


@api_view(["GET"])
def rag_recall(request):
    query = request.query_params.get("query", "")
    assistant = request.query_params.get("assistant")
    from assistants.utils.chunk_retriever import get_relevant_chunks

    chunks, reason, fallback, glossary_present, top_score, _, glossary_forced, *_ = get_relevant_chunks(
        assistant, query
    )
    debug = {
        "reason": reason,
        "fallback": fallback,
        "glossary_present": glossary_present,
        "top_score": top_score,
        "glossary_forced": glossary_forced,
    }
    return Response({"results": chunks, "debug": debug})
