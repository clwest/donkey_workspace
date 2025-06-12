from django.core.management import call_command

def test_rag_replay_runs_without_crash():
    try:
        call_command("replay_rag_query", query="Hello world", assistant="zeno")
    except Exception as exc:
        # Command shouldn't raise unexpected errors
        raise AssertionError(f"Command crashed: {exc}")
