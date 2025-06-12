from django.core.management import call_command
from io import StringIO
import json

def test_rag_replay_runs_without_crash():
    try:
        call_command("replay_rag_query", query="Hello world", assistant="zeno")
    except Exception as exc:
        # Command shouldn't raise unexpected errors
        raise AssertionError(f"Command crashed: {exc}")


def test_rag_replay_outputs_flags():
    out = StringIO()
    call_command("replay_rag_query", query="Hi", assistant="zeno", stdout=out)
    data = json.loads(out.getvalue())
    assert "log" in data
    if data.get("no_chunks"):
        assert "reason" in data or "no_documents" in data
