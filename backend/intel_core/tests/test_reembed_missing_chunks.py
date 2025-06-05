import pytest

from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from intel_core.utils import embedding_debug


@pytest.mark.django_db
def test_reembed_missing_chunks_selects_bad_status(monkeypatch):
    doc = Document.objects.create(title="t", content="c", source_type="text")

    emb1 = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.1])
    emb2 = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.2])

    ch_bad_status = DocumentChunk.objects.create(
        document=doc,
        order=0,
        text="a",
        tokens=1,
        fingerprint="fp1",
        embedding=emb1,
        embedding_status="pending",
    )

    ch_good = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="b",
        tokens=1,
        fingerprint="fp2",
        embedding=emb2,
        embedding_status="embedded",
    )

    ch_missing = DocumentChunk.objects.create(
        document=doc,
        order=2,
        text="c",
        tokens=1,
        fingerprint="fp3",
    )

    calls = []
    monkeypatch.setattr(
        embedding_debug.embed_and_store, "delay", lambda cid: calls.append(cid)
    )

    report = embedding_debug.reembed_missing_chunks()

    assert str(ch_bad_status.id) in calls
    assert str(ch_missing.id) in calls
    assert str(ch_good.id) not in calls
    assert set(report["reprocessed"]) == {str(ch_bad_status.id), str(ch_missing.id)}
