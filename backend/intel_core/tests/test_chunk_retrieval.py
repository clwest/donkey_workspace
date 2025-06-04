import pytest
from unittest.mock import patch

from assistants.models import Assistant
from intel_core.models import Document

class DummyManager(list):
    def select_related(self, *args, **kwargs):
        return self


@patch("assistants.utils.chunk_retriever.get_embedding_for_text", return_value=[0.1])
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity", return_value=0.5)
def test_weak_glossary_filtered(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    weak_chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "SDK refers to Software Development Kit",
            "embedding": type("E", (), {"vector": [0.1]})(),
            "is_glossary": True,
            "glossary_score": 0.1,
        },
    )

    mock_chunk_model.objects.filter.return_value = DummyManager([weak_chunk])

    from assistants.utils.chunk_retriever import get_relevant_chunks

    chunks, *_ = get_relevant_chunks(str(assistant.id), "explain sdk")
    assert chunks == []

    chunks, *_ = get_relevant_chunks(str(assistant.id), "explain sdk", force_fallback=True)
    assert chunks and chunks[0]["chunk_id"] == "1"
