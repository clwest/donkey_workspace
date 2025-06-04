import pytest
from unittest.mock import patch

pytest.importorskip("django")

from assistants.models import Assistant
from memory.models import MemoryEntry
from assistants.utils.delegation_summary_engine import DelegationSummaryEngine


@patch("assistants.utils.delegation_summary_engine.call_llm", return_value="sum")
def test_delegation_summary_fields(mock_llm, db):
    assistant = Assistant.objects.create(name="A", slug="a")
    ctx = assistant.memory_context
    MemoryEntry.objects.create(
        assistant=assistant,
        context=ctx,
        event="delegated task",
        summary="task",
        type="delegation",
    )

    engine = DelegationSummaryEngine(assistant)
    entry = engine.summarize_delegations()
    assert entry.summary == "sum"
    assert entry.full_transcript
    assert "delegated task" in entry.full_transcript
