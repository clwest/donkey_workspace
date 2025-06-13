import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch
import pytest

from assistants.models import Assistant
from assistants.models.reflection import ReflectionGroup
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from mcp_core.models import DevDoc
from memory.models import MemoryEntry
from embeddings.models import Embedding, EmbeddingDebugTag


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


@pytest.mark.django_db
@patch(
    "assistants.utils.assistant_reflection_engine.AssistantReflectionEngine.reflect_on_document",
    return_value=("summary", [], None),
)
def test_reflect_on_document_slug(mock_reflect):
    doc = Document.objects.create(title="Paper", slug="paper", content="x")
    call_command("reflect_on_document", "--doc", "paper")
    mock_reflect.assert_called_once()


@pytest.mark.django_db
@patch(
    "assistants.utils.assistant_reflection_engine.AssistantReflectionEngine.reflect_on_document",
    return_value=("summary", [], None),
)
def test_reflect_on_document_devdoc(mock_reflect):
    doc = Document.objects.create(title="Doc", slug="doc", content="x")
    devdoc = DevDoc.objects.create(title="Doc", slug="doc", linked_document=doc)
    call_command("reflect_on_document", "--doc", devdoc.slug)
    mock_reflect.assert_called_once()


@pytest.mark.django_db
@patch(
    "embeddings.utils.link_repair.repair_context_embeddings",
    return_value={"scanned": 1, "fixed": 1, "skipped": 0},
)
def test_repair_context_embeddings_cli(mock_repair):
    assistant = Assistant.objects.create(
        name="A", slug="a", memory_context_id="11111111-1111-1111-1111-111111111111"
    )
    call_command("repair_context_embeddings", "--assistant", "a")
    mock_repair.assert_called_once_with(assistant.memory_context_id, verbose=True)


@pytest.mark.django_db
@patch("embeddings.management.commands.repair_flagged_embeddings.repair_embedding_link")
@patch("embeddings.management.commands.repair_flagged_embeddings.embedding_link_matches", return_value=True)
def test_repair_flagged_embeddings_cli(mock_match, mock_repair):
    emb = Embedding.objects.create(content_type=None, object_id="x", content_id="x", embedding=[0])
    EmbeddingDebugTag.objects.create(embedding=emb, reason="bad")
    call_command("repair_flagged_embeddings")
    mock_repair.assert_called_once()


@pytest.mark.django_db
@patch("embeddings.management.commands.repair_all_embeddings.FixContext.handle")
@patch("embeddings.management.commands.repair_all_embeddings.FixFlagged.handle")
@patch("embeddings.management.commands.repair_all_embeddings.FixLinks.handle")
@patch("embeddings.management.commands.repair_all_embeddings.FixContent.handle")
def test_repair_all_embeddings_cli(mock_content, mock_links, mock_flagged, mock_context):
    call_command("repair_all_embeddings", "--assistant", "slug")
    mock_content.assert_called_once_with(limit=None)
    mock_links.assert_called_once_with(limit=None)
    mock_flagged.assert_called_once_with()
    mock_context.assert_called_once_with(assistant="slug")


@pytest.mark.django_db
@patch(
    "assistants.utils.assistant_reflection_engine.AssistantReflectionEngine.reflect_on_document",
    return_value=("summary", [], None),
)
def test_reflect_on_document_with_assistant_id(mock_reflect):
    doc = Document.objects.create(title="Paper", content="x")
    assistant = Assistant.objects.create(name="A", slug="a")
    call_command("reflect_on_document", "--doc", str(doc.id), "--assistant", str(assistant.id))
    mock_reflect.assert_called_once()


@pytest.mark.django_db
@patch("assistants.utils.reflection_summary.summarize_reflections_for_document")
def test_summarize_reflection_group_id(mock_sum):
    assistant = Assistant.objects.create(name="A", slug="a")
    group = ReflectionGroup.objects.create(assistant=assistant, slug="grp")
    call_command("summarize_reflection_group", "--group", str(group.id))
    mock_sum.assert_called_once_with(group_slug=group.slug, assistant_id=group.assistant_id)


@pytest.mark.django_db
@patch("assistants.utils.reflection_summary.summarize_reflections_for_document")
def test_summarize_reflection_group_cli(mock_sum):
    assistant = Assistant.objects.create(name="A", slug="a")
    group = ReflectionGroup.objects.create(assistant=assistant, slug="grp")
    call_command("summarize_reflection_group", "--group", "grp")
    mock_sum.assert_called_once_with(
        group_slug=group.slug, assistant_id=group.assistant_id
    )
