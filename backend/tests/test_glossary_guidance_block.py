import pytest
from unittest.mock import patch

pytest.importorskip("django")

from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk
from memory.models import SymbolicMemoryAnchor
from utils import llm_router


@patch("utils.llm_router.call_llm", return_value="ok")
@patch("utils.llm_router.get_relevant_chunks")
def test_guidance_block_injected(mock_get, mock_call, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)
    anchor = SymbolicMemoryAnchor.objects.create(slug="zk-rollup", label="ZK")
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="ZK-Rollup refers to Zero Knowledge Rollup",
        tokens=5,
        fingerprint="fp1",
        is_glossary=True,
        anchor=anchor,
    )
    chunk_info = {
        "chunk_id": str(chunk.id),
        "score": 0.7,
        "text": chunk.text,
        "source_doc": doc.title,
        "is_glossary": True,
        "anchor_slug": anchor.slug,
        "anchor_confidence": 1.0,
    }
    mock_get.return_value = ([chunk_info], None, False, True, 0.7, str(chunk.id), False, False, [])

    llm_router.chat([{"role": "user", "content": "Explain"}], assistant)
    called_msgs = mock_call.call_args[0][0]
    block = next(m["content"] for m in called_msgs if m["role"] == "user" and "MEMORY CHUNKS" in m["content"])
    assert "# Glossary Reference:" in block
    assert "Use this to inform your answer" in block
