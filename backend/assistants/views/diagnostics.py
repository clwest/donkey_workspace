from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import SymbolicMemoryAnchor, MemoryEntry
from intel_core.models import DocumentChunk


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_diagnostics(request, slug):
    """Return diagnostic stats for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    context_id = assistant.memory_context_id
    orphaned_memory_count = MemoryEntry.objects.filter(
        assistant=assistant, context__isnull=True
    ).count()
    reflections_total = AssistantReflectionLog.objects.filter(
        assistant=assistant
    ).count()

    anchors_total = SymbolicMemoryAnchor.objects.count()
    anchors_with_matches = (
        SymbolicMemoryAnchor.objects.filter(chunks__isnull=False)
        .distinct()
        .count()
    )
    anchors_without_matches = anchors_total - anchors_with_matches

    chunks = DocumentChunk.objects.filter(document__linked_assistants=assistant)
    high = chunks.filter(score__gte=0.8).count()
    medium = chunks.filter(score__gte=0.4, score__lt=0.8).count()
    low = chunks.filter(score__lt=0.4).count()

    data = {
        "assistant_id": str(assistant.id),
        "context_id": context_id,
        "orphaned_memory_count": orphaned_memory_count,
        "reflections_total": reflections_total,
        "anchors_total": anchors_total,
        "anchors_with_matches": anchors_with_matches,
        "anchors_without_matches": anchors_without_matches,
        "chunk_score_distribution": {
            "high": high,
            "medium": medium,
            "low": low,
        },
    }
    return Response(data)
