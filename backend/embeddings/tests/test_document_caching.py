# Stub Django cache before importing the module
import sys
import types


# Create a dummy cache to simulate Redis
class DummyCache:
    def __init__(self):
        self.store = {}

    def set(self, key, value, timeout=None):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)


dummy_cache = DummyCache()
# Stub django.core.cache.cache
django_mod = types.ModuleType("django")
django_core = types.ModuleType("django.core")
cache_mod = types.ModuleType("django.core.cache")
cache_mod.cache = dummy_cache
sys.modules["django"] = django_mod
sys.modules["django.core"] = django_core
sys.modules["django.core.cache"] = cache_mod

import json
import logging
import pytest

import embeddings.document_services.document_caching as dc


@pytest.fixture(autouse=True)
def clear_cache():
    # Reset dummy cache before each test
    dummy_cache.store.clear()


def test_get_cached_embedding_none_initial():
    # No embedding cached yet
    assert dc.get_cached_embedding("doc1") is None


def test_cache_and_get_document_embedding():
    doc_id = "doc1"
    emb = [1.23, 4.56]
    # Cache and retrieve
    dc.cache_document_embedding(doc_id, emb)
    got = dc.get_cached_embedding(doc_id)
    assert isinstance(got, list)
    assert got == emb


def test_get_cached_embedding_error(monkeypatch, caplog):
    # Simulate cache.get raising an exception
    def bad_get(key):
        raise ValueError("cache broken")

    fake = types.SimpleNamespace(get=bad_get, set=dummy_cache.set)
    monkeypatch.setattr(dc, "cache", fake)
    caplog.set_level(logging.ERROR, logger="embeddings")
    result = dc.get_cached_embedding("doc2")
    assert result is None
    assert "Error retrieving cached embedding" in caplog.text


def test_session_tracking_and_retrieval():
    session_id = "sess1"
    # Initially no docs
    assert dc.get_session_docs(session_id) == []
    # Track multiple docs
    dc.track_session_usage(session_id, "d1")
    assert dc.get_session_docs(session_id) == ["d1"]
    dc.track_session_usage(session_id, "d2")
    assert dc.get_session_docs(session_id) == ["d1", "d2"]
    # Duplicate should not be appended again
    dc.track_session_usage(session_id, "d2")
    assert dc.get_session_docs(session_id) == ["d1", "d2"]


def test_get_session_docs_error(monkeypatch, caplog):
    # Simulate cache.get raising error
    def bad_get(key):
        raise RuntimeError("oops")

    fake = types.SimpleNamespace(get=bad_get, set=lambda *a, **k: None)
    monkeypatch.setattr(dc, "cache", fake)
    caplog.set_level(logging.ERROR, logger="embeddings")
    assert dc.get_session_docs("sess2") == []
    assert "Error retrieving session docs" in caplog.text
