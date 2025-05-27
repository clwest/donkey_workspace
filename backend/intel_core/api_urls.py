from rest_framework.routers import DefaultRouter
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

urlpatterns = router.urls
