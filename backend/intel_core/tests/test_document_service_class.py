import sys
import types
import os
import django
from unittest.mock import MagicMock

import pytest

sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = lambda: None
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
sys.modules.setdefault("spacy", spacy_stub)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
django.setup()

from intel_core.services import DocumentService
from intel_core.models import Document
from assistants.models.assistant import Assistant


@pytest.mark.django_db
def test_document_service_ingest_url(monkeypatch):
    dummy_doc = Document(title="t", content="c")

    def fake_loader(
        urls, user_provided_title=None, project_name="General", session_id=None
    ):
        return [dummy_doc]

    monkeypatch.setattr("intel_core.processors.url_loader.load_urls", fake_loader)

    result = DocumentService.ingest(
        source_type="url",
        urls=["http://example.com"],
        assistant_id=None,
        project_id=None,
        title="t",
        project_name="general",
    )
    assert result[0]["document_id"] == str(dummy_doc.id)


@pytest.mark.django_db
def test_document_service_ingest_youtube(monkeypatch):
    dummy_doc = Document(title="t", content="c")

    def fake_loader(
        video_urls, user_provided_title=None, project_name="General", session_id=None
    ):
        return [dummy_doc]

    monkeypatch.setattr(
        "intel_core.processors.video_loader.load_videos", fake_loader
    )

    result = DocumentService.ingest(
        source_type="youtube",
        urls=["https://youtu.be/test"],
        assistant_id=None,
        project_id=None,
        title="t",
        project_name="general",
    )
    assert result[0]["document_id"] == str(dummy_doc.id)


@pytest.mark.django_db
def test_ingest_assigns_memory_context(monkeypatch):
    assistant = Assistant.objects.create(name="Bot", description="d", specialty="s")
    doc = Document.objects.create(title="t", content="c")

    def fake_loader(urls, user_provided_title=None, project_name="General", session_id=None):
        return [doc]

    monkeypatch.setattr("intel_core.processors.url_loader.load_urls", fake_loader)

    DocumentService.ingest(
        source_type="url",
        urls=["http://example.com"],
        assistant_id=str(assistant.id),
        project_id=None,
        title="t",
        project_name="general",
    )

    doc.refresh_from_db()
    assert doc.memory_context == assistant.memory_context
