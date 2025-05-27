"""Tests covering embedding generation retry logic."""

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
def test_embedding_retry_logic(monkeypatch):
    """``save_document_to_db`` should retry embedding generation once."""

    calls = []

    class FakeTransformer:
        def encode(self, text):
            calls.append(1)
            return [0.1] if len(calls) > 1 else None

    monkeypatch.setattr(processing, "sentence_transformer", FakeTransformer())
    monkeypatch.setattr(processing, "save_embedding", lambda *a, **k: "ok")
    monkeypatch.setattr(processing, "generate_summary", lambda text: "s")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: None)

    doc = processing.save_document_to_db("some content here", {"title": "t"})

    assert doc is not None
    assert len(calls) == 2
