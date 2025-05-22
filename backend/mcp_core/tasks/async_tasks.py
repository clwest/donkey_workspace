from celery import shared_task
import json

@shared_task(bind=True)
def reflect_on_memories_task(self, user_id, target_type=None, since=None, limit=10):
    from django.contrib.auth import get_user_model
    from agents.utils.agent_reflection_engine import AgentReflectionEngine
    from mcp_core.models import Tag
    from assistants.models import AssistantReflectionLog
    from embeddings.helpers.helpers_io import save_embedding
    from mcp_core.serializers import ReflectionLogSerializer
    user = None
    if user_id:
        user = get_user_model().objects.get(id=user_id)
    agent = AgentReflectionEngine(user=user)
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
    return ReflectionLogSerializer(reflection).data

@shared_task(bind=True)
def suggest_continuity_task(self, thread_id):
    from mcp_core.utils.thread_helpers import suggest_continuity
    from mcp_core.models import NarrativeThread
    from mcp_core.serializers_tags import NarrativeThreadSerializer

    thread = NarrativeThread.objects.get(id=thread_id)
    result = suggest_continuity(thread_id)
    thread._link_suggestions = result.get("link_suggestions", [])
    serializer = NarrativeThreadSerializer(thread)
    data = serializer.data
    data.update(result)
    return data

@shared_task(bind=True)
def realign_thread_task(self, thread_id):
    from mcp_core.models import NarrativeThread
    from assistants.models import AssistantThoughtLog
    from assistants.utils.planning_alignment import suggest_planning_realignment
    from mcp_core.serializers_tags import ThreadDiagnosticLogSerializer
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
    serializer = ThreadDiagnosticLogSerializer(log)
    return serializer.data
