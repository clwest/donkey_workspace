import pytest
from unittest.mock import patch
from io import StringIO

pytest.importorskip("django")

from django.core.management import call_command
from assistants.models import Assistant
from memory.models import MemoryEntry
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine


@patch("assistants.utils.assistant_reflection_engine.call_llm", return_value="ok")
@patch("assistants.utils.assistant_reflection_engine.get_relevant_chunks", return_value=([],))
@patch("assistants.utils.assistant_reflection_engine.generate_embedding", return_value=None)
@patch("assistants.utils.assistant_reflection_engine.save_embedding")
def test_debug_command_shows_valid_memories(mock_save, mock_emb, mock_chunks, mock_llm, db):
    assistant = Assistant.objects.create(name="A", slug="a")
    engine = AssistantReflectionEngine(assistant)
    ctx = assistant.memory_context
    # valid
    MemoryEntry.objects.create(event="e1", summary="s1", importance=2, assistant=assistant, context=ctx)
    MemoryEntry.objects.create(event="e2", full_transcript="t", importance=1, assistant=assistant, context=ctx)
    MemoryEntry.objects.create(event="e3", summary="s3", importance=5, assistant=assistant, context=ctx)
    # junk
    MemoryEntry.objects.create(event="couldn’t find that information", importance=3, assistant=assistant, context=ctx, full_transcript="x")
    MemoryEntry.objects.create(event="low", summary="z", importance=0, assistant=assistant, context=ctx)
    MemoryEntry.objects.create(event="missing", assistant=assistant, context=ctx)

    out = StringIO()
    call_command("debug_reflection_candidates", assistant="a", stdout=out)
    output = out.getvalue()
    assert "Reflection Candidates: 3 valid" in output
    assert "e1" in output and "e2" in output and "e3" in output


@patch("assistants.utils.assistant_reflection_engine.call_llm", return_value="done")
@patch("assistants.utils.assistant_reflection_engine.get_relevant_chunks", return_value=([],))
@patch("assistants.utils.assistant_reflection_engine.generate_embedding", return_value=None)
@patch("assistants.utils.assistant_reflection_engine.save_embedding")
def test_reflect_now_generates_log(mock_save, mock_emb, mock_chunks, mock_llm, db):
    assistant = Assistant.objects.create(name="B", slug="b")
    engine = AssistantReflectionEngine(assistant)
    ctx = assistant.memory_context
    MemoryEntry.objects.create(event="v1", summary="s1", importance=2, assistant=assistant, context=ctx)
    log = engine.reflect_now(verbose=True)
    assert log is not None
    assert log.summary == "done"
