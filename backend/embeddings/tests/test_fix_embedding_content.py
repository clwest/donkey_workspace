import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.core.management import call_command
from embeddings.models import Embedding
from intel_core.models import Document, DocumentChunk
import pytest

pytest.importorskip("django")


@pytest.mark.django_db
def test_fix_embedding_content_command():
    doc = Document.objects.create(title="Doc", content="text")
    chunk = DocumentChunk.objects.create(
        document=doc, order=1, text="chunk text", tokens=2, fingerprint="x"
    )
    emb = Embedding.objects.create(
        content_type=None,
        object_id=str(chunk.id),
        content_id=str(chunk.id),
        content="namespace(content_type='document_chunk', id='{}')".format(chunk.id),
        embedding=[0.1] * 1536,
    )

    call_command("fix_embedding_content")

    emb.refresh_from_db()
    assert emb.content == "chunk text"
