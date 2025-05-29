import pytest
from unittest.mock import patch

pytest.importorskip("django")

from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk, GlossaryFallbackReflectionLog
from memory.models import SymbolicMemoryAnchor
from utils import llm_router


@patch("utils.llm_router.call_llm", side_effect=["I couldn't find that information in the provided memory.", "final"])
@patch("utils.llm_router.get_relevant_chunks")
def test_fallback_logged_and_retry(mock_get, mock_call, db):
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
        "score": 0.8,
        "text": chunk.text,
        "source_doc": doc.title,
        "is_glossary": True,
        "anchor_slug": anchor.slug,
        "anchor_confidence": 1.0,
    }
    mock_get.return_value = ([chunk_info], None, False, True, 0.8, str(chunk.id), False, False, [])

    reply, _, _ = llm_router.chat(
        [{"role": "user", "content": "Explain"}],
        assistant,
        retry_on_miss=True,
    )

    log = GlossaryFallbackReflectionLog.objects.first()
    assert log and log.anchor_slug == "zk-rollup"
    assert log.chunk_id == str(chunk.id)
    assert log.glossary_injected
    assert reply == "final"
    assert mock_call.call_count == 2
