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
router.register(r"embeddings", EmbeddingMetadataViewSet)
router.register(r"embedding-metadata", EmbeddingMetadataViewSet, basename="embeddingmetadata")

urlpatterns = router.urls
