import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from memory.models import SymbolicMemoryAnchor, ChunkTag

pytest.importorskip("django")


@patch("embeddings.helpers.helpers_io.get_embedding_for_text", return_value=[0.1])
@patch("embeddings.vector_utils.compute_similarity", return_value=0.9)
@pytest.mark.django_db
def test_relink_anchor_chunks_links(mock_sim, mock_embed):
    a = Assistant.objects.create(name="A", slug="a")
    doc = Document.objects.create(title="D", content="t")
    emb = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.1])
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="sample",
        tokens=5,
        fingerprint="f1",
        embedding=emb,
        embedding_status="embedded",
    )
    anchor = SymbolicMemoryAnchor.objects.create(slug="term", label="Term")

    call_command("relink_anchor_chunks", "--threshold", "0.2")

    assert ChunkTag.objects.filter(chunk=chunk, name="term").exists()


@patch("embeddings.helpers.helpers_io.get_embedding_for_text", return_value=[0.1])
@patch("embeddings.vector_utils.compute_similarity", return_value=0.9)
@pytest.mark.django_db
def test_relink_anchor_chunks_dry_run(mock_sim, mock_embed):
    anchor = SymbolicMemoryAnchor.objects.create(slug="x", label="X")
    doc = Document.objects.create(title="D2", content="t")
    emb = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.1])
    DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="x",
        tokens=5,
        fingerprint="f2",
        embedding=emb,
        embedding_status="embedded",
    )
    out = StringIO()
    call_command("relink_anchor_chunks", "--dry-run", stdout=out)
    assert "Would create" in out.getvalue()
    assert ChunkTag.objects.count() == 0


@patch("embeddings.helpers.helpers_io.get_embedding_for_text", return_value=[0.1])
@patch("embeddings.vector_utils.compute_similarity", return_value=0.9)
@pytest.mark.django_db
def test_relink_anchor_chunks_purge(mock_sim, mock_embed):
    anchor = SymbolicMemoryAnchor.objects.create(slug="y", label="Y")
    doc = Document.objects.create(title="D3", content="t")
    emb = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.1])
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="y",
        tokens=5,
        fingerprint="f3",
        embedding=emb,
        embedding_status="embedded",
    )
    ChunkTag.objects.create(chunk=chunk, name="y")
    call_command("relink_anchor_chunks", "--purge-existing")
    assert ChunkTag.objects.filter(name="y").count() == 1
