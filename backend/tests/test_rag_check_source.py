import pytest
from unittest.mock import patch

pytest.importorskip("django")

from django.test import Client
from assistants.models import Assistant
from intel_core.models import Document, EmbeddingMetadata


@patch("assistants.utils.chunk_retriever.get_embedding_for_text", return_value=[0.1])
@patch("assistants.utils.chunk_retriever.compute_similarity", return_value=0.9)
@patch("assistants.utils.chunk_retriever.DocumentChunk")
def test_check_source_returns_debug(mock_chunk_model, mock_sim, mock_embed, db):
    client = Client()
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="text")
    assistant.documents.add(doc)
    emb = EmbeddingMetadata.objects.create(vector=[0.1])
    chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "text",
            "embedding": emb,
            "fingerprint": "fp1",
        },
    )
    mock_chunk_model.objects.filter.return_value = [chunk]

    resp = client.post(
        "/api/rag/check-source/",
        data={"assistant_id": assistant.id, "content": "text"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data and len(data["results"]) == 1
    assert "debug" in data and "anchor_boost" in data["debug"]


@patch("assistants.utils.chunk_retriever.get_embedding_for_text", return_value=[0.1])
@patch("assistants.utils.chunk_retriever.compute_similarity", return_value=0.9)
@patch("assistants.utils.chunk_retriever.DocumentChunk")
def test_check_source_accepts_slug(mock_chunk_model, mock_sim, mock_embed, db):
    client = Client()
    assistant = Assistant.objects.create(name="A", slug="assist-a")
    doc = Document.objects.create(title="D", content="text")
    assistant.documents.add(doc)
    emb = EmbeddingMetadata.objects.create(vector=[0.1])
    chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "text",
            "embedding": emb,
            "fingerprint": "fp1",
        },
    )
    mock_chunk_model.objects.filter.return_value = [chunk]

    resp = client.post(
        "/api/rag/check-source/",
        data={"assistant_id": assistant.slug, "content": "text"},
    )
    assert resp.status_code == 200
