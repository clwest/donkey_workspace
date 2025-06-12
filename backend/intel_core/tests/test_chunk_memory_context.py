import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

import uuid
import pytest
from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk

pytest.importorskip("django")


@pytest.mark.django_db
def test_chunk_signal_sets_document_context():
    assistant = Assistant.objects.create(name="SigBot", specialty="s")
    doc = Document.objects.create(title="D", content="c")
    doc.linked_assistants.add(assistant)
    assert doc.memory_context is None
    DocumentChunk.objects.create(
        document=doc,
        order=0,
        text="hello",
        tokens=5,
        fingerprint=str(uuid.uuid4()),
    )
    doc.refresh_from_db()
    assert doc.memory_context == assistant.memory_context
