import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType
from embeddings.models import Embedding, EmbeddingDriftLog, EmbeddingDebugTag
from intel_core.models import Document, DocumentChunk
import pytest
import uuid

pytest.importorskip("django")


@pytest.mark.django_db
def test_log_embedding_drift():
    doc = Document.objects.create(title="Doc", content="x")
    chunk = DocumentChunk.objects.create(
        document=doc, order=1, text="chunk", tokens=1, fingerprint=str(uuid.uuid4())
    )
    emb = Embedding.objects.create(
        content_type=None,
        object_id=str(chunk.id),
        content_id="wrong:{}".format(chunk.id),
        embedding=[0.1] * 5,
    )
    EmbeddingDebugTag.objects.create(embedding=emb, reason="wrong FK", repair_status="repaired")
    call_command("log_embedding_drift")
    assert EmbeddingDriftLog.objects.count() > 0
