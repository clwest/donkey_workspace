from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import SymbolicMemoryAnchor, MemoryEntry
from mcp_core.models import MemoryContext
from intel_core.models import DocumentChunk
from intel_core.utils.glossary_tagging import retag_glossary_chunks
from assistants.utils.assistant_boot import (
    generate_boot_profile,
    run_assistant_self_test,
    run_batch_self_tests,
)


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


@api_view(["POST"])
@permission_classes([AllowAny])
def fix_context(request, slug):
    """Link orphaned memories to the assistant's context."""
    assistant = get_object_or_404(Assistant, slug=slug)
    context = assistant.memory_context
    if not context:
        context, _ = MemoryContext.objects.get_or_create(
            content=f"{assistant.slug} context"
        )
        assistant.memory_context = context
        assistant.save(update_fields=["memory_context"])

    count = MemoryEntry.objects.filter(assistant=assistant, context__isnull=True).update(
        context=context
    )
    return Response({"updated": count, "context_id": context.id})


@api_view(["POST"])
@permission_classes([AllowAny])
def retag_glossary_chunks_view(request, slug):
    """Retag chunks for the assistant using glossary anchors."""
    assistant = get_object_or_404(Assistant, slug=slug)
    results = retag_glossary_chunks(assistant)
    total = sum(len(v) for v in results.values())
    summary = {k: len(v) for k, v in results.items()}
    return Response({"matched_total": total, "per_anchor": summary})

@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_boot_profile(request, slug):
    """Return boot profile diagnostics for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    data = generate_boot_profile(assistant)
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def assistant_self_test(request, slug):
    """Run a lightweight self-test for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    result = run_assistant_self_test(assistant)
    return Response(result)


@api_view(["POST"])
@permission_classes([AllowAny])
def run_all_self_tests(request):
    """Run boot self-tests for all assistants."""
    results = run_batch_self_tests()
    return Response({"status": "ok", "results": results})
