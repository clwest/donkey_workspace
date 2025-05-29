from unittest.mock import patch

import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from intel_core.models import Document
from memory.models import SymbolicMemoryAnchor
from utils import llm_router


@patch("utils.llm_router.call_llm", return_value="ok")
@patch("utils.llm_router.get_relevant_chunks")
def test_glossary_line_added(mock_get, mock_call, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    chunks = [
        {
            "chunk_id": "1",
            "score": 0.6,
            "text": "ZK-Rollup refers to Zero Knowledge Rollup",
            "source_doc": "D",
            "is_glossary": True,
            "anchor_slug": "zk-rollup",
            "anchor_confidence": 1.0,
        }
    ]
    mock_get.return_value = (chunks, None, False, True, 0.6, "1", False, False, [])

    llm_router.chat([{"role": "user", "content": "What is a zk-rollup?"}], assistant)
    called_msgs = mock_call.call_args[0][0]
    system_msg = next(m["content"] for m in called_msgs if m["role"] == "system")
    assert "You have access to glossary definitions" in system_msg


@patch("utils.llm_router.call_llm", return_value="ok")
@patch("utils.llm_router.get_relevant_chunks")
def test_anchor_guidance_injected(mock_get, mock_call, db):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)
    anchor = SymbolicMemoryAnchor.objects.create(
        slug="zk-rollup",
        label="ZK",
        glossary_guidance="If the user asks about performance, use this definition.",
    )
    chunks = [
        {
            "chunk_id": "1",
            "score": 0.6,
            "text": "ZK-Rollup refers to Zero Knowledge Rollup",
            "source_doc": "D",
            "is_glossary": True,
            "anchor_slug": anchor.slug,
            "anchor_confidence": 1.0,
        }
    ]
    mock_get.return_value = (chunks, None, False, True, 0.6, "1", False, False, [])

    llm_router.chat([{"role": "user", "content": "What is a zk-rollup?"}], assistant)
    called_msgs = mock_call.call_args[0][0]
    system_msg = next(m["content"] for m in called_msgs if m["role"] == "system")
    assert "If the user asks about performance" in system_msg
