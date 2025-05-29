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
            "text_preview": c.text[:300],
        }
        for c in chunks
    ]
    return Response(out)
