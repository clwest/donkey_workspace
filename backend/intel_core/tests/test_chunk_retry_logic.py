import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
import django
django.setup()

import sys
import types
from unittest.mock import patch
import pytest

sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = lambda: None
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
sys.modules.setdefault("spacy", spacy_stub)

import intel_core.utils.processing as processing
from intel_core.models import DocumentChunk, DocumentProgress


@pytest.mark.django_db
def test_retry_with_short_candidates(monkeypatch):
    monkeypatch.setattr(processing, "get_embedding_for_text", lambda text: [0.1])
    monkeypatch.setattr(processing, "save_embedding", lambda *a, **k: "id")
    monkeypatch.setattr(processing, "generate_summary", lambda text: "s")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: None)
    monkeypatch.setattr(processing, "generate_chunks", lambda text: ["a short", "b short"])
    monkeypatch.setattr(processing, "generate_chunk_fingerprint", lambda text: f"fp_{hash(text)}")
    monkeypatch.setattr(
        processing,
        "clean_and_score_chunk",
        lambda t, chunk_index=None: {"text": t, "score": 0.1, "keep": False, "reason": "too_short"},
    )
    with patch("intel_core.utils.processing.embed_and_store.delay") as mock_delay:
        doc = processing.save_document_to_db("word " * 60, {"title": "T", "source_type": "pdf"})

    chunks = DocumentChunk.objects.filter(document=doc)
    assert chunks.count() > 0
    meta = doc.metadata
    assert meta.get("chunk_retry_attempts") == 1
    progress = DocumentProgress.objects.get(progress_id=meta["progress_id"])
    assert "retry_attempts:1" in progress.error_message
    assert not meta.get("chunk_retry_needed", False)


@pytest.mark.django_db
def test_retry_bypass_filters(monkeypatch):
    monkeypatch.setattr(processing, "get_embedding_for_text", lambda text: [0.1])
    monkeypatch.setattr(processing, "save_embedding", lambda *a, **k: "id")
    monkeypatch.setattr(processing, "generate_summary", lambda text: "s")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: None)
    monkeypatch.setattr(processing, "generate_chunks", lambda text: ["bad chunk"])
    monkeypatch.setattr(processing, "generate_chunk_fingerprint", lambda text: f"fp_{hash(text)}")
    monkeypatch.setattr(
        processing,
        "clean_and_score_chunk",
        lambda t, chunk_index=None: {"text": t, "score": 0.0, "keep": False, "reason": "low_quality"},
    )
    with patch("intel_core.utils.processing.embed_and_store.delay") as mock_delay:
        doc = processing.save_document_to_db("word " * 60, {"title": "T2", "source_type": "pdf"})

    chunks = DocumentChunk.objects.filter(document=doc)
    assert chunks.count() > 0
    meta = doc.metadata
    assert meta.get("chunk_retry_attempts") == 1
    progress = DocumentProgress.objects.get(progress_id=meta["progress_id"])
    assert "retry_attempts:1" in progress.error_message
    assert not meta.get("chunk_retry_needed", False)
