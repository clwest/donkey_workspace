import pytest
from unittest.mock import patch

pytest.importorskip("django")

from embeddings.tasks import embed_and_store
from intel_core.models import Document, DocumentChunk


def test_embed_and_store_marks_failed_on_empty_embedding(db, caplog):
    doc = Document.objects.create(title="Doc", content="text")
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="part",
        tokens=1,
        fingerprint="fp1",
    )

    with patch("embeddings.tasks.generate_embedding", return_value=[]):
        caplog.set_level("INFO", logger="embeddings")
        result = embed_and_store(str(chunk.id))

    chunk.refresh_from_db()
    assert result is None
    assert chunk.embedding_status == "failed"
    assert "[Chunk Failed]" in caplog.text


def test_embed_and_store_saves_chunk_text(db):
    doc = Document.objects.create(title="Doc", content="text")
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="hello world",
        tokens=2,
        fingerprint="fp2",
    )

    vector = [0.1] * 1536
    with patch("embeddings.tasks.generate_embedding", return_value=vector), patch(
        "embeddings.tasks.verify_chunk_embedding.delay"
    ):
        emb_id = embed_and_store(str(chunk.id))

    from embeddings.models import Embedding

    emb = Embedding.objects.get(id=emb_id)
    assert emb.content == "hello world"

