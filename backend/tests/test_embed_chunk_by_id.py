import pytest
from unittest.mock import patch

pytest.importorskip("django")

from django.core.management import call_command
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata


@patch("intel_core.management.commands.embed_chunk_by_id.embed_and_store.delay")
@patch(
    "intel_core.management.commands.embed_chunk_by_id.compute_glossary_score",
    return_value=(0.6, ["mcp"]),
)
def test_embed_chunk_by_id_updates_chunk(mock_score, mock_delay, db):
    doc = Document.objects.create(title="T", content="body")
    emb = EmbeddingMetadata.objects.create(
        model_used="m",
        num_tokens=1,
        vector=[0.0] * 1536,
        status="completed",
        source="test",
    )
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="MCP refers to Model Context Protocol",
        tokens=5,
        fingerprint="fp1",
        embedding=emb,
        embedding_status="embedded",
        glossary_score=0.0,
        is_glossary=True,
    )

    call_command("embed_chunk_by_id", id=str(chunk.id))

    mock_delay.assert_called_once_with(str(chunk.id))
    chunk.refresh_from_db()
    assert chunk.embedding is None
    assert chunk.embedding_status == "pending"
    assert chunk.glossary_score == 0.6
    assert chunk.matched_anchors == ["mcp"]
