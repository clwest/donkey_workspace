from rest_framework import viewsets

from .models import Document, DocumentChunk, EmbeddingMetadata
from .serializers import (
    DocumentSerializer,
    DocumentChunkSerializer,
    EmbeddingMetadataSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-created_at")
    serializer_class = DocumentSerializer


class DocumentChunkViewSet(viewsets.ModelViewSet):
    queryset = DocumentChunk.objects.all().order_by("order")
    serializer_class = DocumentChunkSerializer


class EmbeddingMetadataViewSet(viewsets.ModelViewSet):
    queryset = EmbeddingMetadata.objects.all().order_by("-created_at")
    serializer_class = EmbeddingMetadataSerializer
