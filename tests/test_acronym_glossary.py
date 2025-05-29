import pytest

from intel_core.services.acronym_glossary_service import AcronymGlossaryService


def test_glossary_injection():
    chunks = ["MCP powers our stack"]
    result = AcronymGlossaryService.insert_glossary_chunk(chunks.copy())
    assert result[0].startswith("MCP refers to Model Context Protocol")
    assert len(result) == 2


from unittest.mock import patch
from assistants.utils.chunk_retriever import get_relevant_chunks
from assistants.models import Assistant
from intel_core.models import Document


class DummyManager(list):
    def select_related(self, *args, **kwargs):
        return self


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_prefers_longform(
    mock_sim, mock_chunk_model, mock_embed, db
):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="text")
    assistant.documents.add(doc)

    long_chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "MCP refers to Model Context Protocol, a secure pattern",
            "embedding": type("E", (), {"vector": [0.1]})(),
        },
    )
    short_chunk = type(
        "C",
        (),
        {
            "id": 2,
            "document_id": doc.id,
            "document": doc,
            "text": "MCP only",
            "embedding": type("E", (), {"vector": [0.2]})(),
        },
    )
    manager = DummyManager([long_chunk, short_chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.side_effect = [0.6, 0.6]

    chunks, *_ = get_relevant_chunks(str(assistant.id), "What is MCP?")
    assert chunks[0]["chunk_id"] == "1"
    assert "Model Context Protocol" in chunks[0]["text"]


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_glossary_score_boost(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="text")
    assistant.documents.add(doc)

    glossary_chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "SDK refers to Software Development Kit",
            "embedding": type("E", (), {"vector": [0.1]})(),
            "is_glossary": True,
            "tags": ["glossary"],
        },
    )
    other_chunk = type(
        "C",
        (),
        {
            "id": 2,
            "document_id": doc.id,
            "document": doc,
            "text": "random text",
            "embedding": type("E", (), {"vector": [0.1]})(),
        },
    )
    manager = DummyManager([other_chunk, glossary_chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.side_effect = [0.5, 0.5]

    chunks, *_ = get_relevant_chunks(str(assistant.id), "What is SDK?")
    assert chunks[0]["chunk_id"] == "1"


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_anchor_forces_injection(mock_sim, mock_chunk_model, mock_embed, db):
    from memory.models import SymbolicMemoryAnchor

    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="text")
    assistant.documents.add(doc)
    anchor = SymbolicMemoryAnchor.objects.create(slug="sdk", label="SDK", is_focus_term=True)

    glossary_chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "SDK refers to Software Development Kit",
            "embedding": type("E", (), {"vector": [0.1]})(),
            "is_glossary": True,
            "anchor": anchor,
        },
    )
    manager = DummyManager([glossary_chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.3

    chunks, reason, fallback, _, _, _, _, _, _ = get_relevant_chunks(
        str(assistant.id), "explain sdk"
    )
    assert chunks[0]["chunk_id"] == "1"
    assert fallback is True
    assert reason == "forced anchor"
    assert chunks[0].get("override_reason") == "anchor-match"
