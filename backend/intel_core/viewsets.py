from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Document, DocumentChunk, EmbeddingMetadata
from .serializers import (
    DocumentSerializer,
    DocumentDetailSerializer,
    DocumentChunkFullSerializer,
    DocumentChunkInfoSerializer,
    EmbeddingMetadataSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DocumentDetailSerializer
        return DocumentSerializer

    @action(detail=True)
    def chunks(self, request, pk=None):
        doc = self.get_object()
        qs = doc.chunks.all().order_by("order")
        if request.query_params.get("skipped") == "true":
            qs = qs.filter(embedding_status="skipped")
        if request.query_params.get("force") == "true":
            qs = qs.filter(force_embed=True)
        status_str = "completed"
        if qs.count() < doc.chunks.count():
            status_str = "processing"
        serializer = DocumentChunkInfoSerializer(qs, many=True)
        return Response({"chunks": serializer.data, "status": status_str})


class DocumentChunkViewSet(viewsets.ModelViewSet):
    queryset = DocumentChunk.objects.all().order_by("order")
    serializer_class = DocumentChunkFullSerializer

    @action(detail=True, methods=["post"])
    def repair(self, request, pk=None):
        chunk = self.get_object()
        from embeddings.document_services.chunking import clean_and_score_chunk
        from embeddings.tasks import embed_and_store

        info = clean_and_score_chunk(chunk.text, chunk_index=chunk.order)
        new_score = info.get("score")
        if new_score is not None:
            chunk.score = new_score
            chunk.save(update_fields=["score"])

        if chunk.embedding_status != "embedded":
            chunk.embedding_status = "pending"
            chunk.save(update_fields=["embedding_status"])
            embed_and_store.delay(str(chunk.id))

        return Response(
            {
                "id": str(chunk.id),
                "status": chunk.embedding_status,
                "score": chunk.score,
            }
        )


class EmbeddingMetadataViewSet(viewsets.ModelViewSet):
    queryset = EmbeddingMetadata.objects.all().order_by("-created_at")
    serializer_class = EmbeddingMetadataSerializer
