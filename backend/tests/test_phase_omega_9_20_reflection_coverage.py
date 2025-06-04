import logging
import pytest
from unittest.mock import patch

pytest.importorskip("django")

from django.core.management import call_command
from assistants.models import Assistant, AssistantReflectionLog
from memory.models import MemoryEntry, SymbolicMemoryAnchor


@patch(
    "assistants.management.commands.reflect_on_self.AssistantReflectionEngine.generate_reflection"
)
def test_reflect_on_self_covers_memories(mock_gen, db, caplog):
    assistant = Assistant.objects.create(name="Scope", slug="scope")
    ctx = assistant.memory_context

    anchor = SymbolicMemoryAnchor.objects.create(slug="term", label="Term")
    MemoryEntry.objects.create(
        assistant=assistant,
        context=ctx,
        event="GLOSSARY_USED",
        summary="term used",
        anchor=anchor,
    )
    MemoryEntry.objects.create(
        assistant=assistant,
        context=ctx,
        event="INGEST_SUMMARY",
        summary="doc summary",
        type="ingest_summary",
    )
    MemoryEntry.objects.create(
        assistant=assistant,
        context=ctx,
        event="Delegation occurred",
        summary="child action",
        type="delegation",
    )

    mock_gen.return_value = (
        "- noted glossary usage\n- recorded ingest summary\n#reflection-scope:complete"
    )

    with caplog.at_level(logging.WARNING):
        call_command("reflect_on_self", assistant=assistant.slug)

    log = AssistantReflectionLog.objects.filter(assistant=assistant).first()
    assert log is not None
    assert "glossary" in log.summary.lower()
    assert "ingest" in log.summary.lower()
    assert "#reflection-scope" in log.summary
    assert any("delegation" in r.getMessage().lower() for r in caplog.records)
