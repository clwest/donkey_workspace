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
def test_repair_embedding_links_command():
    doc = Document.objects.create(title="Doc", content="text")
    chunk = DocumentChunk.objects.create(
        document=doc, order=1, text="chunk", tokens=1, fingerprint=str(uuid.uuid4())
    )
    emb = Embedding.objects.create(
        content_type=None,
        object_id=str(chunk.id),
        content_id="wrong:{}".format(chunk.id),
        embedding=[0.1] * 5,
    )

    call_command("repair_embedding_links")

    emb.refresh_from_db()
    ct = ContentType.objects.get_for_model(DocumentChunk)
    assert emb.content_type == ct
    assert emb.content_id == f"documentchunk:{chunk.id}"
