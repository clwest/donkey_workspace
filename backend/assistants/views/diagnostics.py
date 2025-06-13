from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assistants.models import Assistant
from assistants.models.diagnostics import AssistantDiagnosticReport
from assistants.models.reflection import AssistantReflectionLog
from memory.models import SymbolicMemoryAnchor, MemoryEntry
from mcp_core.models import MemoryContext
from intel_core.models import DocumentChunk
from intel_core.utils.glossary_tagging import retag_glossary_chunks

# ``assistant_boot`` contains generic self-test helpers while
# ``boot_diagnostics`` builds a richer boot profile used by the UI.
from assistants.utils.boot_diagnostics import (
    generate_boot_profile,
    run_assistant_self_test,
)
from assistants.utils.assistant_boot import (
    run_batch_self_tests,
    boot_check,
    repair_assistant_boot,
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
        SymbolicMemoryAnchor.objects.filter(chunks__isnull=False).distinct().count()
    )
    anchors_without_matches = anchors_total - anchors_with_matches

    chunks = DocumentChunk.objects.filter(document__linked_assistants=assistant)
    high = chunks.filter(score__gte=0.8).count()
    medium = chunks.filter(score__gte=0.4, score__lt=0.8).count()
    low = chunks.filter(score__lt=0.4).count()

    from memory.models import RAGGroundingLog

    logs = RAGGroundingLog.objects.filter(assistant=assistant)
    glossary_hit_count = logs.filter(glossary_hits__len__gt=0).count()
    fallback_count = logs.filter(fallback_triggered=True).count()

    data = {
        "assistant_id": str(assistant.id),
        "context_id": context_id,
        "orphaned_memory_count": orphaned_memory_count,
        "reflections_total": reflections_total,
        "anchors_total": anchors_total,
        "anchors_with_matches": anchors_with_matches,
        "anchors_without_matches": anchors_without_matches,
        "glossary_hit_count": glossary_hit_count,
        "fallback_count": fallback_count,
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

    count = MemoryEntry.objects.filter(
        assistant=assistant, context__isnull=True
    ).update(context=context)
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


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_boot_status(request, slug):
    """Return simple boot status flags for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    status = boot_check(assistant)
    chunks = DocumentChunk.objects.filter(document__linked_assistants=assistant)
    total_chunks = chunks.count()
    embedded_chunks = chunks.filter(embedding_status="embedded").count()
    fallback_ratio = (
        chunks.filter(chunk_type="fallback").count() / total_chunks
        if total_chunks
        else 0.0
    )
    status.update(
        {
            "context_id": assistant.memory_context_id,
            "linked_documents": assistant.documents.count(),
            "total_chunks": total_chunks,
            "embedded_chunks": embedded_chunks,
            "fallback_ratio": round(fallback_ratio, 2),
        }
    )
    return Response(status)


@api_view(["POST"])
@permission_classes([AllowAny])
def assistant_self_test(request, slug):
    """Run a lightweight self-test for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    result = run_assistant_self_test(assistant)
    return Response(result)


@api_view(["POST"])
@permission_classes([AllowAny])
def rag_self_test(request, slug):
    """Run glossary-based RAG self-test for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from assistants.utils.rag_diagnostics import run_assistant_rag_test

    limit = None
    if isinstance(request.data, dict) and "limit" in request.data:
        try:
            limit = int(request.data.get("limit"))
        except (TypeError, ValueError):
            limit = None

    try:
        result = run_assistant_rag_test(assistant, limit=limit)
    except Exception as e:  # pragma: no cover - defensive
        return Response({"error": str(e)}, status=400)

    return Response(result)


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_drift_summary(request, slug):
    """Return latest embedding drift summary for the assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from embeddings.models import EmbeddingDriftLog
    from memory.models import RAGGroundingLog
    from django.utils import timezone
    from datetime import timedelta

    logs_qs = EmbeddingDriftLog.objects.filter(
        assistant=assistant,
        timestamp__gte=timezone.now() - timedelta(days=7),
    ).order_by("context_id", "-timestamp")

    last_logged = (
        EmbeddingDriftLog.objects.filter(assistant=assistant)
        .order_by("-timestamp")
        .first()
    )

    contexts = {}
    snapshots = []
    for log in logs_qs:
        cid = str(log.context_id) if log.context_id else None
        snapshots.append(
            {
                "timestamp": log.timestamp,
                "context_id": cid,
                "mismatched": log.mismatched_count,
                "orphaned": log.orphaned_count,
                "repaired": log.repaired_count,
            }
        )
        ctx = contexts.setdefault(
            cid,
            {
                "context_id": cid,
                "mismatched": 0,
                "orphaned": 0,
                "repaired": 0,
                "last_attempt": None,
            },
        )
        ctx["mismatched"] += log.mismatched_count
        ctx["orphaned"] += log.orphaned_count
        ctx["repaired"] += log.repaired_count
        if log.repair_attempted_at and (
            not ctx["last_attempt"] or log.repair_attempted_at > ctx["last_attempt"]
        ):
            ctx["last_attempt"] = log.repair_attempted_at

    total_logs = RAGGroundingLog.objects.filter(assistant=assistant).count()
    hit_count = RAGGroundingLog.objects.filter(
        assistant=assistant, glossary_hits__len__gt=0
    ).count()
    fallback_count = RAGGroundingLog.objects.filter(
        assistant=assistant, fallback_triggered=True
    ).count()

    ratio = (hit_count / total_logs * 100) if total_logs else 0
    fallback_pct = (fallback_count / total_logs * 100) if total_logs else 0

    return Response(
        {
            "contexts": list(contexts.values()),
            "anchor_ratio": ratio,
            "fallback_pct": fallback_pct,
            "logs": snapshots,
            "last_logged": last_logged.timestamp if last_logged else None,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def run_all_self_tests(request):
    """Run boot self-tests for all assistants."""
    results = run_batch_self_tests()
    return Response({"status": "ok", "results": results})


@api_view(["POST"])
@permission_classes([AllowAny])
def repair_assistant_slug(request, slug):
    """Repair boot data for a single assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    changed = repair_assistant_boot(assistant)
    return Response({"updated": changed})


@api_view(["POST"])
@permission_classes([AllowAny])
def summarize_delegations(request, slug):
    """Generate a summary of delegation memories for the assistant."""
    from .utils.delegation_summary_engine import DelegationSummaryEngine

    assistant = get_object_or_404(Assistant, slug=slug)
    engine = DelegationSummaryEngine(assistant)
    entry = engine.summarize_delegations()
    return Response({"summary": entry.summary, "memory_id": str(entry.id)})


@api_view(["POST"])
@permission_classes([AllowAny])
def reflect_on_self(request, slug):
    """Proxy to assistants.self_reflect for stable route name."""
    from .assistants import self_reflect

    return self_reflect(request, slug)


@api_view(["GET"])
@permission_classes([AllowAny])
def subagent_reflect(request, slug, event_id):
    """Proxy to delegations.subagent_reflect using path param."""
    from .delegations import subagent_reflect as _reflect

    return _reflect(request, slug, event_id)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_assistant_diagnostic_report(request, slug):
    """Return the most recent AssistantDiagnosticReport as JSON."""
    assistant = get_object_or_404(Assistant, slug=slug)
    report = (
        AssistantDiagnosticReport.objects.filter(assistant=assistant)
        .order_by("-generated_at")
        .first()
    )
    if not report:
        return Response({}, status=404)
    return Response(
        {
            "slug": report.slug,
            "generated_at": report.generated_at.isoformat(),
            "fallback_rate": report.fallback_rate,
            "glossary_success_rate": report.glossary_success_rate,
            "avg_chunk_score": report.avg_chunk_score,
            "rag_logs_count": report.rag_logs_count,
        }
    )
