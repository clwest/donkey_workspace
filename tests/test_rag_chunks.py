import pytest
from unittest.mock import patch

pytest.importorskip("django")

from assistants.utils.chunk_retriever import get_relevant_chunks
from assistants.models import Assistant
from intel_core.models import Document


class DummyManager(list):
    def select_related(self, *args, **kwargs):
        return self


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_filters(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    chunk1 = type("C", (), {"id": 1, "document_id": doc.id, "document": doc, "text": "keep", "embedding": type("E", (), {"vector": [0.1]})()})
    chunk2 = type("C", (), {"id": 2, "document_id": doc.id, "document": doc, "text": "drop", "embedding": type("E", (), {"vector": [0.2]})()})
    manager = DummyManager([chunk1, chunk2])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.side_effect = [0.8, 0.6]

    chunks, reason, fallback = get_relevant_chunks(str(assistant.id), "q", score_threshold=0.75)
    assert reason is None
    assert fallback is False
    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "1"


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_fallback(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    chunk1 = type("C", (), {"id": 1, "document_id": doc.id, "document": doc, "text": "c1", "embedding": type("E", (), {"vector": [0.1]})()})
    chunk2 = type("C", (), {"id": 2, "document_id": doc.id, "document": doc, "text": "c2", "embedding": type("E", (), {"vector": [0.2]})()})
    manager = DummyManager([chunk1, chunk2])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.side_effect = [0.6, 0.55]

    chunks, reason, fallback = get_relevant_chunks(str(assistant.id), "q", score_threshold=0.75)
    assert fallback is True
    assert reason == "low score"
    assert len(chunks) >= 1
