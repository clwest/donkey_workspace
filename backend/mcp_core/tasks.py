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


@shared_task
def reflect_on_memories_task(payload: dict):
    from assistants.models import AssistantReflectionLog
    from mcp_core.models import Tag
    from agents.utils.agent_reflection_engine import AgentReflectionEngine
    from embeddings.helpers.helpers_io import save_embedding
    import json

    target_type = payload.get("target_type")
    since = payload.get("since")
    limit = int(payload.get("limit", 10))
    agent = AgentReflectionEngine(user=None)
    memories = agent.reflect_on(target_type=target_type, since=since, limit=limit)
    if not memories:
        return {"error": "No important memories found."}
    reflection_out = agent.get_structured_reflection(memories)
    llm_summary = agent.get_llm_summary(memories)
    mood = agent.analyze_mood(llm_summary)
    reflection_data = json.loads(reflection_out)
    reflection = AssistantReflectionLog.objects.create(
        title=reflection_data.get("title", "Untitled Reflection"),
        summary=reflection_data.get("summary", ""),
        llm_summary=llm_summary,
        raw_prompt=agent.summarize_reflection(memories),
        mood=mood,
    )
    if hasattr(reflection, "related_memories"):
        reflection.related_memories.set(memories)
    tag_names = reflection_data.get("tags", [])
    if tag_names:
        tags = Tag.objects.filter(name__in=tag_names)
        reflection.tags.set(tags)
    save_embedding(reflection, embedding=[])
    return reflection.id


@shared_task
def suggest_continuity_task(thread_id: str):
    from mcp_core.utils.thread_helpers import suggest_continuity
    return suggest_continuity(thread_id)


@shared_task
def realign_thread_task(thread_id: str):
    from assistants.models import AssistantThoughtLog
    from mcp_core.serializers_threads import ThreadDiagnosticLogSerializer
    from assistants.utils.planning_alignment import suggest_planning_realignment
    from mcp_core.models import ThreadDiagnosticLog

    thread = NarrativeThread.objects.get(id=thread_id)
    thoughts = (
        AssistantThoughtLog.objects.filter(narrative_thread=thread)
        .order_by("-created_at")[:20]
    )
    suggestion = suggest_planning_realignment(thread, thoughts)
    log = ThreadDiagnosticLog.objects.create(
        thread=thread,
        score=thread.continuity_score or 0.0,
        summary=suggestion["summary"],
        type="realignment_suggestion",
        proposed_changes=suggestion,
    )
    return ThreadDiagnosticLogSerializer(log).data
