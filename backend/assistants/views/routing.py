from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from assistants.utils.delegation_router import suggest_assistants_for_task
from assistants.models import Assistant, RoutingSuggestionLog
from memory.models import MemoryEntry

@api_view(["POST"])
def suggest_assistant(request):
    """Suggest an assistant for the given text or memory."""
    text = request.data.get("text")
    memory_id = request.data.get("memory_id")
    accepted = bool(request.data.get("accepted"))
    user_feedback = request.data.get("user_feedback")

    context_summary = ""
    tags = []
    task = None

    if memory_id:
        memory = MemoryEntry.objects.filter(id=memory_id).first()
        if not memory:
            return Response({"error": "Memory not found"}, status=404)
        task = memory
        context_summary = memory.summary or memory.event or ""
        tags = list(memory.tags.values_list("name", flat=True))
    elif text:
        task = text
        context_summary = str(text)[:200]
    else:
        return Response({"error": "Provide text or memory_id"}, status=400)

    results = suggest_assistants_for_task(task)
    best = results[0] if results else None
    assistant = best["assistant"] if best else None
    score = best["score"] if best else 0.0
    reason = best.get("reason") if best else ""

    log = RoutingSuggestionLog.objects.create(
        context_summary=context_summary,
        tags=tags,
        suggested_assistant=assistant,
        confidence_score=score,
        reasoning=reason,
        selected=accepted,
        user_feedback=user_feedback if accepted else None,
    )

    data = {
        "assistant": assistant.slug if assistant else None,
        "score": score,
        "log_id": str(log.id),
    }
    return Response(data)


@api_view(["GET"])
def routing_history(request):
    """Return routing suggestion logs with optional filters."""
    logs = RoutingSuggestionLog.objects.all()
    tag = request.GET.get("tag")
    assistant = request.GET.get("assistant")
    min_conf = request.GET.get("min_confidence")
    feedback = request.GET.get("feedback")

    if tag:
        logs = logs.filter(tags__contains=[tag])
    if assistant:
        logs = logs.filter(suggested_assistant__slug=assistant)
    if min_conf:
        try:
            logs = logs.filter(confidence_score__gte=float(min_conf))
        except ValueError:
            pass
    if feedback:
        logs = logs.filter(user_feedback=feedback)

    logs = logs.order_by("-timestamp")[:100]
    data = [
        {
            "id": str(l.id),
            "context_summary": l.context_summary,
            "tags": l.tags,
            "assistant": l.suggested_assistant.slug if l.suggested_assistant else None,
            "confidence_score": l.confidence_score,
            "reasoning": l.reasoning,
            "selected": l.selected,
            "user_feedback": l.user_feedback,
            "timestamp": l.timestamp.isoformat(),
        }
        for l in logs
    ]
    return Response({"results": data})
