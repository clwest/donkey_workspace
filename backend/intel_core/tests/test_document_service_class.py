import sys
import types
from unittest.mock import MagicMock

import pytest

sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = lambda: None
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
sys.modules.setdefault("spacy", spacy_stub)

from intel_core.services import DocumentService
from intel_core.models import Document


@pytest.mark.django_db
def test_document_service_ingest_url(monkeypatch):
    dummy_doc = Document(title="t", content="c")

    def fake_loader(
        urls, user_provided_title=None, project_name="General", session_id=None
    ):
        return [dummy_doc]

    monkeypatch.setattr("intel_core.processors.url_loader.load_urls", fake_loader)

    docs = DocumentService.ingest(
        source_type="url",
        urls=["http://example.com"],
        assistant_id=None,
        project_id=None,
        title="t",
        project_name="general",
    )

    assert docs == [dummy_doc]
