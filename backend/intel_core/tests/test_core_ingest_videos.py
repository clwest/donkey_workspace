import sys
import types
import pytest

sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = lambda: None
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
sys.modules.setdefault("spacy", spacy_stub)

from intel_core.models import Document
from core.services import document_service as doc_service


@pytest.mark.django_db
def test_ingest_videos_returns_document(monkeypatch):
    dummy_doc = Document(title="t", content="c")

    monkeypatch.setattr(doc_service, "process_youtube_video", lambda url: ["hello", "world"])
    monkeypatch.setattr(doc_service, "process_videos", lambda *args, **kwargs: dummy_doc)

    result = doc_service.ingest_videos(["https://youtu.be/test"])
    assert result[0]["document_id"] == str(dummy_doc.id)


@pytest.mark.django_db
def test_ingest_videos_returns_skipped(monkeypatch):
    monkeypatch.setattr(doc_service, "process_youtube_video", lambda url: [])
    result = doc_service.ingest_videos(["https://youtu.be/test"])
    assert result[0]["status"] == "skipped"
