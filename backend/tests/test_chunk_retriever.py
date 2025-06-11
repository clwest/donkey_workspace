import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from unittest.mock import patch
from assistants.utils.chunk_retriever import get_relevant_chunks
from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata


@patch("assistants.utils.chunk_retriever.get_embedding_for_text")
@patch("assistants.utils.chunk_retriever.compute_similarity")
def test_basic_chunk_retrieval(mock_sim, mock_embed, db):
    assistant = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
    doc = Document.objects.create(
        title="Reflect Guide", content="text", memory_context=assistant.memory_context
    )
    assistant.documents.add(doc)
    emb = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.1])
    DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="This section helps you reflect on progress",
        tokens=5,
        fingerprint="f1",
        embedding=emb,
        embedding_status="embedded",
    )
    mock_embed.return_value = [0.1]
    mock_sim.return_value = 0.9
    chunks, *_ = get_relevant_chunks(str(assistant.id), "help me reflect")
    assert chunks
    assert chunks[0]["document_id"] == str(doc.id)
