import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch
import pytest

from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from memory.models import MemoryEntry
from embeddings.models import Embedding


pytest.importorskip("django")


@pytest.mark.django_db
def test_repair_rag_chunk_links_command():
    doc = Document.objects.create(title="Doc", content="text")
    chunk = DocumentChunk.objects.create(
        document=doc, order=1, text="body", tokens=1, fingerprint="fp1"
    )
    emb = Embedding.objects.create(
        content_type=None, object_id="xxx", content_id="xxx", embedding=[0.1]
    )
    meta = EmbeddingMetadata.objects.create(
        model_used="m", num_tokens=1, vector=[0.1], embedding=emb
    )
    chunk.embedding = meta
    chunk.save(update_fields=["embedding"])

    assistant = Assistant.objects.create(name="A", slug="a")
    mem = MemoryEntry.objects.create(event="e", assistant=assistant)
    emb2 = Embedding.objects.create(
        content_type=None, object_id="y", content_id="y", embedding=[0.1]
    )
    mem.embeddings.add(emb2)

    call_command("repair_rag_chunk_links")

    emb.refresh_from_db()
    emb2.refresh_from_db()
    ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
    ct_mem = ContentType.objects.get_for_model(MemoryEntry)
    assert emb.object_id == str(chunk.id)
    assert emb.content_type == ct_chunk
    assert emb2.object_id == str(mem.id)
    assert emb2.content_type == ct_mem


@pytest.mark.django_db
def test_infer_glossary_anchors_cli():
    assistant = Assistant.objects.create(name="ClarityBot", slug="claritybot")
    MemoryEntry.objects.create(
        assistant=assistant, event="goal threading", summary="goal threading"
    )

    call_command("infer_glossary_anchors", "--assistant", assistant.slug)

    assert assistant.symbolicmemoryanchor_set.filter(slug="goal-threading").exists()


@pytest.mark.django_db
@patch(
    "assistants.utils.assistant_reflection_engine.AssistantReflectionEngine.reflect_on_document",
    return_value=("summary", [], None),
)
def test_reflect_on_document_cli(mock_reflect):
    doc = Document.objects.create(title="Paper", content="x")
    call_command("reflect_on_document", "--doc", str(doc.id))
    mock_reflect.assert_called_once()

