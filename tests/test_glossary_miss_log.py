from unittest.mock import patch
import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk, GlossaryMissReflectionLog
from memory.models import SymbolicMemoryAnchor
from utils import llm_router


@patch("utils.llm_router.call_llm", return_value="I couldn't find that information in the provided memory.")
@patch("utils.llm_router.get_relevant_chunks")
@patch("utils.llm_router.AssistantThoughtEngine.reflect_on_glossary_gap", return_value="reflection")
def test_glossary_miss_logged(mock_reflect, mock_get, mock_call, db):
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

    llm_router.chat([
        {"role": "user", "content": "What’s the gas cost difference?"}
    ], assistant)

    log = GlossaryMissReflectionLog.objects.first()
    assert log is not None
    assert log.anchor == anchor
    assert chunk in log.matched_chunks.all()
    assert log.reflection == "reflection"
