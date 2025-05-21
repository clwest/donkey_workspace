from celery import shared_task

from mcp_core.models import NarrativeThread
from mcp_core.utils.thread_diagnostics import run_thread_diagnostics


@shared_task
def analyze_mood_impact_on_thread_continuity(thread_id: str):
    """Run diagnostics and mood analysis for a thread."""
    try:
        thread = NarrativeThread.objects.get(id=thread_id)
    except NarrativeThread.DoesNotExist:
        return "thread not found"
    run_thread_diagnostics(thread)
    return "ok"
