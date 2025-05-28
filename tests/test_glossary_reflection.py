from unittest.mock import patch

import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from intel_core.models import Document
from utils import llm_router


@patch("utils.llm_router.call_llm", return_value="ok")
@patch("utils.llm_router.get_relevant_chunks")
@patch("utils.llm_router.AssistantThoughtEngine.reflect_on_rag_failure")
def test_reflection_logged_when_glossary_fallback(
    mock_reflect, mock_get, mock_call, db
):
    assistant = Assistant.objects.create(name="A")
    doc = Document.objects.create(title="D", content="txt")
    assistant.documents.add(doc)

    mock_get.return_value = ([], "low", False, True, 0.2, None)

    llm_router.chat([{"role": "user", "content": "What is SDK"}], assistant)
    mock_reflect.assert_called_once()
