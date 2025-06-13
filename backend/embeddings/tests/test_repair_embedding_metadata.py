import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType
from embeddings.models import Embedding
from intel_core.models import Document, DocumentChunk
import pytest
import uuid

pytest.importorskip("django")


@pytest.mark.django_db
def test_repair_embedding_metadata_from_chunk():
    doc = Document.objects.create(title="Doc", content="x", source_type="pdf")
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="c",
        tokens=1,
        fingerprint=str(uuid.uuid4()),
    )
    ct = ContentType.objects.get_for_model(DocumentChunk)
    emb = Embedding.objects.create(
        content_type=ct,
        object_id=str(chunk.id),
        content_id=f"documentchunk:{chunk.id}",
        embedding=[0.1] * 5,
    )

    call_command("repair_embedding_metadata")

    emb.refresh_from_db()
    assert str(emb.session_id) == str(doc.session_id)
    assert emb.source_type == doc.source_type


@pytest.mark.django_db
def test_repair_embedding_metadata_from_document():
    doc = Document.objects.create(title="Doc2", content="y", source_type="url")
    ct = ContentType.objects.get_for_model(Document)
    emb = Embedding.objects.create(
        content_type=ct,
        object_id=str(doc.id),
        content_id=f"document:{doc.id}",
        embedding=[0.1] * 5,
        session_id=None,
        source_type=None,
    )

    call_command("repair_embedding_metadata")

    emb.refresh_from_db()
    assert str(emb.session_id) == str(doc.session_id)
    assert emb.source_type == doc.source_type
