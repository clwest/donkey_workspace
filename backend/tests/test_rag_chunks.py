import pytest
from unittest.mock import patch

pytest.importorskip("django")

from assistants.utils.chunk_retriever import get_relevant_chunks
from assistants.models import Assistant
from intel_core.models import (
    Document,
    DocumentChunk,
    EmbeddingMetadata,
)
from mcp_core.models import MemoryContext
from memory.models import MemoryEntry, SymbolicMemoryAnchor


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

    chunk1 = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "keep",
            "embedding": type("E", (), {"vector": [0.1]})(),
        },
    )
    chunk2 = type(
        "C",
        (),
        {
            "id": 2,
            "document_id": doc.id,
            "document": doc,
            "text": "drop",
            "embedding": type("E", (), {"vector": [0.2]})(),
        },
    )
    manager = DummyManager([chunk1, chunk2])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.side_effect = [0.8, 0.6]

    chunks, reason, fallback, _, _, _, _, _, _, _ = get_relevant_chunks(
        str(assistant.id), "q", score_threshold=0.75
    )
    assert reason is None
    assert fallback is False
    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "1"


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_unembedded_chunks_ignored(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    c1 = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "valid",
            "embedding": type("E", (), {"vector": [0.1]})(),
            "embedding_status": "embedded",
        },
    )
    c2 = type(
        "C",
        (),
        {
            "id": 2,
            "document_id": doc.id,
            "document": doc,
            "text": "pending",
            "embedding": type("E", (), {"vector": [0.2]})(),
            "embedding_status": "pending",
        },
    )
    manager = DummyManager([c1, c2])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.side_effect = [0.9, 0.8]

    chunks, *_ = get_relevant_chunks(str(assistant.id), "q")
    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "1"


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_fallback(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    chunk1 = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "c1",
            "embedding": type("E", (), {"vector": [0.1]})(),
        },
    )
    chunk2 = type(
        "C",
        (),
        {
            "id": 2,
            "document_id": doc.id,
            "document": doc,
            "text": "c2",
            "embedding": type("E", (), {"vector": [0.2]})(),
        },
    )
    manager = DummyManager([chunk1, chunk2])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.side_effect = [0.6, 0.55]

    chunks, reason, fallback, _, _, _, _, _, _, _ = get_relevant_chunks(
        str(assistant.id), "q", score_threshold=0.75
    )
    assert fallback is True
    assert reason == "low score"
    assert len(chunks) >= 1


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_lowest_scores(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "c1",
            "embedding": type("E", (), {"vector": [0.1]})(),
        },
    )
    manager = DummyManager([chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.2

    chunks, reason, fallback, _, _, _, _, _, _, _ = get_relevant_chunks(
        str(assistant.id), "q", score_threshold=0.75
    )
    assert fallback is True
    assert len(chunks) >= 1


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_project_filter(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    project = assistant.projects.create(title="P")
    project.documents.add(doc)

    chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "c",
            "embedding": type("E", (), {"vector": [0.2]})(),
        },
    )
    manager = DummyManager([chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.9

    chunks, *_ = get_relevant_chunks(None, "q", project_id=str(project.id))
    assert len(chunks) == 1
    assert chunks[0]["document_id"] == str(doc.id)


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_document_filter(
    mock_sim, mock_chunk_model, mock_embed, db
):
    doc = Document.objects.create(title="D", content="txt")
    chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "c",
            "embedding": type("E", (), {"vector": [0.2]})(),
        },
    )
    manager = DummyManager([chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.9

    chunks, *_ = get_relevant_chunks(None, "q", document_id=str(doc.id))
    assert len(chunks) == 1
    assert chunks[0]["document_id"] == str(doc.id)


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_context_filter(mock_sim, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    ctx1 = assistant.memory_context
    ctx2 = MemoryContext.objects.create(content="Other")

    doc1 = Document.objects.create(title="D1", content="t1", memory_context=ctx1)
    doc2 = Document.objects.create(title="D2", content="t2", memory_context=ctx2)
    assistant.documents.add(doc1, doc2)

    emb1 = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.1])
    chunk1 = DocumentChunk.objects.create(
        document=doc1,
        order=1,
        text="c1",
        tokens=5,
        fingerprint="f1",
        embedding=emb1,
        embedding_status="embedded",
    )
    emb2 = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.2])
    DocumentChunk.objects.create(
        document=doc2,
        order=1,
        text="c2",
        tokens=5,
        fingerprint="f2",
        embedding=emb2,
        embedding_status="embedded",
    )

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.9

    chunks, *_ = get_relevant_chunks(
        str(assistant.id),
        "q",
        memory_context_id=str(ctx1.id),
    )
    assert len(chunks) == 1
    assert chunks[0]["document_id"] == str(doc1.id)


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_reflection_terms_boosted(mock_sim, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    ctx = assistant.memory_context

    anchor = SymbolicMemoryAnchor.objects.create(slug="evm", label="EVM")
    doc = Document.objects.create(title="D", content="text", memory_context=ctx)
    assistant.documents.add(doc)
    emb = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.1])
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="EVM explained",
        tokens=5,
        fingerprint="f3",
        anchor=anchor,
        embedding=emb,
        embedding_status="embedded",
    )
    MemoryEntry.objects.create(
        assistant=assistant,
        context=ctx,
        event="reflection",
        summary="Discussion of evm details",
        type="reflection",
        linked_content_type=None,
    )

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.5

    chunks, _, _, _, top_score, top_id, *_ = get_relevant_chunks(
        str(assistant.id),
        "what is evm",
        memory_context_id=str(ctx.id),
    )

    assert top_id == str(chunk.id)
    assert top_score > 0.5


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_get_relevant_chunks_force_keyword(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "intro",
            "embedding": type("E", (), {"vector": [0.1]})(),
        },
    )
    manager = DummyManager([chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.2

    query = "What was the opening line?"
    chunks, reason, fallback, _, _, _, _, _, _, _ = get_relevant_chunks(
        str(assistant.id), query, score_threshold=0.75
    )
    assert len(chunks) == 1
    assert fallback is True


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_anchor_boost(mock_sim, mock_chunk_model, mock_embed, db):
    from memory.models import SymbolicMemoryAnchor

    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)
    anchor = SymbolicMemoryAnchor.objects.create(
        slug="rag", label="RAG", is_focus_term=True
    )

    anchor_chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "retrieval augmented generation",
            "embedding": type("E", (), {"vector": [0.1]})(),
            "anchor": anchor,
        },
    )
    other_chunk = type(
        "C",
        (),
        {
            "id": 2,
            "document_id": doc.id,
            "document": doc,
            "text": "other",
            "embedding": type("E", (), {"vector": [0.1]})(),
        },
    )
    manager = DummyManager([other_chunk, anchor_chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.side_effect = [0.4, 0.4]

    chunks, *_ = get_relevant_chunks(str(assistant.id), "tell me about rag")
    assert chunks[0]["chunk_id"] == "1"


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_non_focus_anchor_ignored(mock_sim, mock_chunk_model, mock_embed, db):
    from memory.models import SymbolicMemoryAnchor

    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)
    anchor = SymbolicMemoryAnchor.objects.create(slug="sdk", label="SDK")

    chunk = type(
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
    manager = DummyManager([chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.3

    chunks, *_ = get_relevant_chunks(str(assistant.id), "what is sdk")
    assert chunks == []


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_anchor_weight_profile(mock_sim, mock_chunk_model, mock_embed, db):
    from memory.models import SymbolicMemoryAnchor
    from assistants.utils import chunk_retriever

    assistant = Assistant.objects.create(name="A", anchor_weight_profile={"evm": 0.5})
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)
    anchor = SymbolicMemoryAnchor.objects.create(
        slug="evm", label="EVM", is_focus_term=True
    )

    anchor_chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "evm text",
            "embedding": type("E", (), {"vector": [0.1]})(),
            "anchor": anchor,
        },
    )
    other_chunk = type(
        "C",
        (),
        {
            "id": 2,
            "document_id": doc.id,
            "document": doc,
            "text": "other",
            "embedding": type("E", (), {"vector": [0.1]})(),
        },
    )
    manager = DummyManager([other_chunk, anchor_chunk])
    mock_chunk_model.objects.filter.return_value = manager

    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.4

    with patch.object(chunk_retriever, "ANCHOR_BOOST", 0):
        chunks, *_ = chunk_retriever.get_relevant_chunks(str(assistant.id), "q")
    assert chunks[0]["chunk_id"] == "1"



@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.DocumentChunk")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_excludes_non_embedded_chunks(mock_sim, mock_chunk_model, mock_embed, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    embedded_chunk = type(
        "C",
        (),
        {
            "id": 1,
            "document_id": doc.id,
            "document": doc,
            "text": "ok",
            "embedding": type("E", (), {"vector": [0.1]})(),
            "embedding_status": "embedded",
        },
    )

    pending_chunk = type(
        "C",
        (),
        {
            "id": 2,
            "document_id": doc.id,
            "document": doc,
            "text": "pending",
            "embedding": type("E", (), {"vector": [0.2]})(),
            "embedding_status": "pending",
        },
    )

    captured_kwargs = {}

    def fake_filter(*args, **kwargs):
        captured_kwargs.update(kwargs)
        # Only return the embedded chunk, mimicking DB filter
        return DummyManager([embedded_chunk])

    mock_chunk_model.objects.filter.side_effect = fake_filter
    mock_embed.return_value = [0.5]
    mock_sim.return_value = 0.8

    chunks, *_ = get_relevant_chunks(str(assistant.id), "q")

    assert captured_kwargs.get("embedding_status") == "embedded"
    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "1"


