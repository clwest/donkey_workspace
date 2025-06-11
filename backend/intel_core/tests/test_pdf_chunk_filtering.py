import sys
import types
from unittest.mock import patch

import pytest

# Stub external libs
sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = lambda: None
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
sys.modules.setdefault("spacy", spacy_stub)

import intel_core.utils.processing as processing
from intel_core.models import DocumentChunk


@pytest.mark.django_db
def test_long_pdf_generates_chunks(monkeypatch):
    monkeypatch.setattr(processing, "get_embedding_for_text", lambda text: [0.1])
    monkeypatch.setattr(processing, "save_embedding", lambda *a, **k: "id")
    monkeypatch.setattr(processing, "generate_summary", lambda text: "s")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: None)

    content = "\n\n".join(f"Paragraph {i}. short." for i in range(350))
    content += "\n\nFigure 1\n\nReferences\n\n[1] Example."
    metadata = {"title": "Long PDF", "source_type": "pdf"}

    with patch("intel_core.utils.processing.embed_and_store.delay") as mock_delay:
        doc = processing.save_document_to_db(content, metadata)

    chunks = DocumentChunk.objects.filter(document=doc)
    assert chunks.count() >= 10
    assert mock_delay.call_count == chunks.count()
