import pytest
from unittest.mock import patch

pytest.importorskip("django")

from django.core.management import call_command
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


@patch("assistants.management.commands.repair_delegation_summaries.DelegationSummaryEngine._compress_history", return_value="short")
def test_repair_delegation_full_transcript(mock_compress, mock_llm, db):
    assistant = Assistant.objects.create(name="B", slug="b")
    ctx = assistant.memory_context
    mem = MemoryEntry.objects.create(
        assistant=assistant,
        context=ctx,
        event="child summary",
        type="delegation_summary",
        summary=None,
        full_transcript=None,
    )

    call_command("repair_delegation_summaries", assistant=assistant.slug)

    mem.refresh_from_db()
    assert mem.summary.startswith("child summary")
    assert mem.full_transcript
