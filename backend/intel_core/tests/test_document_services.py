"""Integration tests for document ingestion utilities."""

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


import intel_core.utils.ingestion as ingestion
import intel_core.utils.processing as processing
from intel_core.models import Document
from assistants.models import Topic
from mcp_core.models import Tag


@pytest.mark.django_db
def test_end_to_end_pipeline(monkeypatch):
    """Ingest a simple URL and ensure a Document instance is returned."""

    dummy_doc = Document(title="t", content="c")

    def fake_loader(urls, user_provided_title=None, project_name="General", session_id=None):
        return [dummy_doc]

    monkeypatch.setattr("intel_core.processors.url_loader.load_urls", fake_loader)

    docs = ingestion.ingest_urls(["http://example.com"], title="t")
    assert docs == [dummy_doc]


@pytest.mark.django_db
def test_save_document_assigns_embedding_and_tag(monkeypatch):
    """Verify embedding generation and tag assignment occur."""

    Topic.objects.create(name="sports", keywords="sport,game")
    tag = Tag.objects.create(name="sports", slug="sports")

    emb_mock = MagicMock()
    emb_mock.encode.return_value = [0.1, 0.2]
    save_mock = MagicMock(return_value="emb123")

    monkeypatch.setattr(processing, "sentence_transformer", emb_mock)
    monkeypatch.setattr(processing, "save_embedding", save_mock)
    monkeypatch.setattr(processing, "generate_summary", lambda text: "summary")
    monkeypatch.setattr(processing, "clean_text", lambda text: text)
    monkeypatch.setattr(processing, "lemmatize_text", lambda text, nlp: text)
    monkeypatch.setattr(processing, "detect_topic", lambda text: "sports")

    doc = processing.save_document_to_db("sport game content", {"title": "test", "source_type": "url"})

    assert doc is not None
    emb_mock.encode.assert_called()
    save_mock.assert_called_once()
    assert doc.tags.filter(id=tag.id).exists()
