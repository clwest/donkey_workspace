from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import chunks
from .viewsets import (
    DocumentViewSet,
    DocumentChunkViewSet,
    EmbeddingMetadataViewSet,
)

router = DefaultRouter()
router.register(r"documents", DocumentViewSet)
router.register(r"chunks", DocumentChunkViewSet, basename="chunk")
router.register(r"document-chunks", DocumentChunkViewSet, basename="documentchunk")
# Primary embeddings endpoint
router.register(r"embeddings", EmbeddingMetadataViewSet, basename="embeddingmetadata")
# Alias maintained for backward compatibility
router.register(
    r"embedding-metadata",
    EmbeddingMetadataViewSet,
    basename="embeddingmetadataalias",
)
urlpatterns = [
    path("chunk-stats/", chunks.chunk_stats, name="chunk_stats"),
] + router.urls
