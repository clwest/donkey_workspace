from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import DelegationEvent, Assistant
from assistants.models.thoughts import AssistantThoughtLog
from assistants.serializers import DelegationEventSerializer
from assistants.utils.delegation import spawn_delegated_assistant
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
from assistants.utils.delegation_summary_engine import DelegationSummaryEngine
from memory.services import MemoryService
from intel_core.models import Document
from assistants.models.project import AssistantObjective


@api_view(["GET"])
def recent_delegation_events(request):
    """Return the 25 most recent delegation events."""
    events = DelegationEvent.objects.select_related(
        "parent_assistant",
        "child_assistant",
        "triggering_memory",
        "triggering_session",
    ).order_by("-created_at")[:25]
    serializer = DelegationEventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def spawn_from_context(request, slug):
    """Spawn a delegated assistant using the provided context."""
    parent = get_object_or_404(Assistant, slug=slug)

    ctx_type = request.data.get("context_type")
    ctx_id = request.data.get("context_id")
    reason = request.data.get("reason", "delegation")

    memory_entry = None
    if ctx_type == "memory" and ctx_id:
        memory_entry = MemoryService.get_entry_or_404(ctx_id)
    elif ctx_type == "document" and ctx_id:
        document = get_object_or_404(Document, id=ctx_id)
        memory_entry = MemoryService.create_entry(
            event=f"Spawn from document {document.title}",
            summary=document.summary or document.title,
            document=document,
            assistant=parent,
        )
    else:
        return Response({"error": "Invalid context"}, status=400)

    child = spawn_delegated_assistant(parent, memory_entry=memory_entry, reason=reason)
    return Response(
        {
            "slug": child.slug,
            "tone": child.inherited_tone,
            "created_from_mood": child.created_from_mood,
        },
        status=201,
    )


@api_view(["POST"])
def delegation_event_feedback(request, id):
    """Attach feedback to a delegation event."""
    event = get_object_or_404(DelegationEvent, id=id)
    score = request.data.get("score")
    trust_label = request.data.get("trust_label")
    notes = request.data.get("notes")

    if score is not None:
        try:
            event.score = int(score)
        except (TypeError, ValueError):
            pass
    if trust_label in {"trusted", "neutral", "unreliable"}:
        event.trust_label = trust_label
    if notes is not None:
        event.notes = notes

    event.save()
    return Response({"success": True})


@api_view(["POST"])
def delegate_from_objective(request, slug, objective_id):
    """Delegate an objective to a new assistant."""
    parent = get_object_or_404(Assistant, slug=slug)
    objective = get_object_or_404(AssistantObjective, id=objective_id)

    engine = AssistantThoughtEngine(assistant=parent)
    child = engine.delegate_objective(objective)

    return Response({"slug": child.slug}, status=201)


@api_view(["POST"])
def suggest_delegate(request):
    """Return ranked assistants for a memory or text."""
    memory_id = request.data.get("memory_id")
    text = request.data.get("text")
    slug = request.data.get("assistant_slug")

    memory = None
    if memory_id:
        memory = MemoryService.get_entry(memory_id)
        if not memory:
            return Response({"error": "Memory not found"}, status=404)

    if not memory and not text:
        return Response({"error": "Provide memory_id or text"}, status=400)

    from assistants.utils.delegation_router import suggest_assistants_for_task

    task_text = text or memory.summary or memory.event
    results = suggest_assistants_for_task(memory or task_text)

    data = [
        {
            "slug": r["assistant"].slug,
            "name": r["assistant"].name,
            "score": round(r["score"], 3),
        }
        for r in results
    ]

    if slug:
        parent = Assistant.objects.filter(slug=slug).first()
        if parent:
            summary = ", ".join(f"{d['name']} - {d['score']:.2f}" for d in data)
            AssistantThoughtLog.objects.create(
                assistant=parent,
                thought_type="delegation_suggestion",
                thought=f"Delegation suggestions: {summary}",
                linked_memory=memory,
            )

    return Response({"suggestions": data})

@api_view(["POST"])
def summarize_delegations(request, slug):
    """Generate a summary of delegation memories."""
    assistant = get_object_or_404(Assistant, slug=slug)
    engine = DelegationSummaryEngine(assistant)
    entry = engine.summarize_delegations()
    return Response({"summary": entry.event, "memory_id": str(entry.id)})
