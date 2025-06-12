import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

import pytest
from embeddings.models import Embedding
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata

pytest.importorskip("django")

@pytest.mark.django_db
def test_embedding_metadata_links_to_embedding():
    doc = Document.objects.create(title="D", content="t")
    chunk = DocumentChunk.objects.create(document=doc, order=1, text="c", tokens=1, fingerprint="f")
    emb = Embedding.objects.create(content_type=None, object_id=str(chunk.id), content_id="documentchunk:%s" % chunk.id, embedding=[0.1])
    meta = EmbeddingMetadata.objects.create(embedding_id=emb.id, embedding=emb, model_used="m", num_tokens=1, vector=[0.1])
    chunk.embedding = meta
    chunk.save(update_fields=["embedding"])
    assert meta.embedding == emb
    assert meta.chunk == chunk
