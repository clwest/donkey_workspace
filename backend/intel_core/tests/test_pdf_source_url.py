import sys
import types
from unittest.mock import MagicMock

import pytest

sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = lambda: None
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
sys.modules.setdefault("spacy", spacy_stub)

numpy_stub = types.ModuleType("numpy")
class FakeNdArray(list):
    pass
numpy_stub.ndarray = FakeNdArray
sys.modules.setdefault("numpy", numpy_stub)

import intel_core.utils.processing as processing


@pytest.mark.django_db
def test_missing_source_url_placeholder(monkeypatch):
    """Document save should succeed even when source_url not provided."""

    class DummyTransformer:
        def encode(self, text):
            return [0.1, 0.2]

    monkeypatch.setattr(processing, "sentence_transformer", DummyTransformer())
    monkeypatch.setattr(processing, "save_embedding", lambda *a, **k: "id")
    monkeypatch.setattr(processing, "generate_summary", lambda text: "s")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: None)

    metadata = {"title": "PDF Doc", "source_type": "pdf"}
    doc = processing.save_document_to_db("some pdf content", metadata)

    assert doc is not None
    assert doc.source_url.startswith("uploaded://")

