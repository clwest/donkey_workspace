from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Document, DocumentChunk, EmbeddingMetadata
from .serializers import (
    DocumentSerializer,
    DocumentDetailSerializer,
    DocumentChunkSerializer,
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
        serializer = DocumentChunkInfoSerializer(qs, many=True)
        return Response(serializer.data)


class DocumentChunkViewSet(viewsets.ModelViewSet):
    queryset = DocumentChunk.objects.all().order_by("order")
    serializer_class = DocumentChunkSerializer


class EmbeddingMetadataViewSet(viewsets.ModelViewSet):
    queryset = EmbeddingMetadata.objects.all().order_by("-created_at")
    serializer_class = EmbeddingMetadataSerializer
