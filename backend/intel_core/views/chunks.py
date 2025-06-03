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
