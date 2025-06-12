import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from intel_core.services import DocumentService
from intel_core.models import Document


def test_document_assignment_on_ingest(db, monkeypatch):
    dummy_doc = Document(title="doc", content="c")

    def fake_loader(
        urls, user_provided_title=None, project_name="General", session_id=None
    ):
        return [dummy_doc]

    monkeypatch.setattr("intel_core.processors.url_loader.load_urls", fake_loader)

    assistant = Assistant.objects.create(name="A")
    result = DocumentService.ingest(
        source_type="url",
        urls=["http://example.com"],
        assistant_id=str(assistant.id),
        project_name="general",
        title="doc",
    )
    assert result[0]["document_id"] == str(dummy_doc.id)
    assert assistant.assigned_documents.filter(id=dummy_doc.id).exists()
    dummy_doc.refresh_from_db()
    assert dummy_doc.memory_context_id == assistant.memory_context_id
