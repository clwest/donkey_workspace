from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from intel_core.models import Document, DocumentChunk, DocumentProgress
from intel_core.serializers import DocumentChunkSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def document_chunks(request, doc_id):
    """Return chunk metadata for a document."""
    qs = DocumentChunk.objects.filter(document_id=doc_id).order_by("order")
    if request.query_params.get("skipped") == "true":
        qs = qs.filter(embedding_status="skipped")
    if qs.exists():
        serializer = DocumentChunkSerializer(qs, many=True)
        return Response({"chunks": serializer.data, "status": "completed"})

    progress = DocumentProgress.objects.filter(progress_id=doc_id).first()
    if progress:
        return Response({"chunks": [], "status": progress.status})

    # Document may exist but no chunks yet
    if Document.objects.filter(id=doc_id).exists():
        return Response({"chunks": [], "status": "processing"})

    return Response({"chunks": []})


@api_view(["GET"])
@permission_classes([AllowAny])
def chunk_stats(request):
    """Return basic score distribution for a document."""
    doc_id = request.query_params.get("document_id")
    if not doc_id:
        return Response({"error": "document_id required"}, status=400)
    document = Document.objects.filter(id=doc_id).first()
    if not document:
        return Response({"error": "Document not found"}, status=404)
    qs = DocumentChunk.objects.filter(document=document)
    distribution = {}
    for ch in qs:
        key = f"{ch.score:.2f}"
        distribution[key] = distribution.get(key, 0) + 1
    glossary_hits = qs.filter(is_glossary=True).count()
    anchor_counts = {}
    for ch in qs:
        for slug in ch.matched_anchors:
            anchor_counts[slug] = anchor_counts.get(slug, 0) + 1
    return Response(
        {
            "document": str(document.id),
            "distribution": distribution,
            "glossary_hits": glossary_hits,
            "chunk_total": qs.count(),
            "anchor_counts": anchor_counts,
        }
    )
