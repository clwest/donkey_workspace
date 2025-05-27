from rest_framework.routers import DefaultRouter
from .viewsets import (
    DocumentViewSet,
    DocumentChunkViewSet,
    EmbeddingMetadataViewSet,
)

router = DefaultRouter()
router.register(r"documents", DocumentViewSet)
router.register(r"chunks", DocumentChunkViewSet)
router.register(r"embeddings", EmbeddingMetadataViewSet)

urlpatterns = router.urls
