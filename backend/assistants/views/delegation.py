from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import DelegationEvent, Assistant
from assistants.serializers import DelegationEventSerializer
from assistants.utils.delegation import spawn_delegated_assistant
from memory.models import MemoryEntry
from intel_core.models import Document


@api_view(["GET"])
def recent_delegation_events(request):
    """Return the 25 most recent delegation events."""
    events = (
        DelegationEvent.objects.select_related(
            "parent_assistant",
            "child_assistant",
            "triggering_memory",
            "triggering_session",
        )
        .order_by("-created_at")[:25]
    )
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
        memory_entry = get_object_or_404(MemoryEntry, id=ctx_id)
    elif ctx_type == "document" and ctx_id:
        document = get_object_or_404(Document, id=ctx_id)
        memory_entry = MemoryEntry.objects.create(
            event=f"Spawn from document {document.title}",
            summary=document.summary or document.title,
            document=document,
            assistant=parent,
        )
    else:
        return Response({"error": "Invalid context"}, status=400)

    child = spawn_delegated_assistant(parent, memory_entry=memory_entry, reason=reason)
    return Response({"slug": child.slug}, status=201)
