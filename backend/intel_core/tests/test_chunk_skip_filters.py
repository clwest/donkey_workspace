import os
import sys
import types
from unittest.mock import patch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

import pytest

sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = lambda: None
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
sys.modules.setdefault("spacy", spacy_stub)

import intel_core.utils.processing as processing
from intel_core.models import DocumentChunk


@pytest.mark.django_db
def test_skip_short_chunk(monkeypatch):
    monkeypatch.setattr(processing, "get_embedding_for_text", lambda text: [0.1])
    monkeypatch.setattr(processing, "save_embedding", lambda *a, **k: "id")
    monkeypatch.setattr(processing, "generate_summary", lambda text: "s")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: None)

    monkeypatch.setattr(processing, "generate_chunks", lambda text: ["hi", "long enough chunk to keep"])
    monkeypatch.setattr(processing, "generate_chunk_fingerprint", lambda text: f"fp_{hash(text)}")
    monkeypatch.setattr(processing, "clean_and_score_chunk", lambda t, chunk_index=None: {"text": t, "score": 1.0 if len(t.split()) > 2 else 0.0, "keep": len(t.split()) > 2, "reason": "ok" if len(t.split()) > 2 else "too_short"})

    doc = processing.save_document_to_db("x" * 120, {"title": "t", "source_type": "url"})
    assert doc is not None
    assert DocumentChunk.objects.filter(document=doc).count() == 1


@pytest.mark.django_db
def test_duplicate_fingerprint_skipped(monkeypatch):
    monkeypatch.setattr(processing, "get_embedding_for_text", lambda text: [0.1])
    monkeypatch.setattr(processing, "save_embedding", lambda *a, **k: "id")
    monkeypatch.setattr(processing, "generate_summary", lambda text: "s")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: None)

    monkeypatch.setattr(processing, "generate_chunks", lambda text: ["duplicate chunk one", "duplicate chunk two"])
    monkeypatch.setattr(processing, "generate_chunk_fingerprint", lambda text: "samefp")
    monkeypatch.setattr(processing, "clean_and_score_chunk", lambda t, chunk_index=None: {"text": t, "score": 1.0, "keep": True, "reason": "ok"})

    doc = processing.save_document_to_db("y" * 120, {"title": "dup", "source_type": "url"})
    assert doc is not None
    assert DocumentChunk.objects.filter(document=doc).count() == 1
