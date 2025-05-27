import sys
import types

import pytest

sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = lambda: None
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
sys.modules.setdefault("spacy", spacy_stub)

import intel_core.utils.processing as processing
from intel_core.models import DocumentChunk


@pytest.mark.django_db
def test_document_chunks_have_embeddings(monkeypatch):
    """Save text and ensure chunks have embeddings."""

    monkeypatch.setattr(processing, "generate_embedding", lambda text: [0.1])
    monkeypatch.setattr(processing, "save_embedding", lambda *a, **k: "id")
    monkeypatch.setattr(processing, "generate_summary", lambda text: "summary")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: None)

    content = "a" * 1100
    doc = processing.save_document_to_db(
        content,
        {"title": "Chunk Test", "source_type": "url"},
    )
    assert doc is not None

    chunks = DocumentChunk.objects.filter(document=doc)
    assert chunks.exists()
    for chunk in chunks:
        assert chunk.embedding is not None
