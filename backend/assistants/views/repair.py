from django.shortcuts import get_object_or_404
from uuid import uuid4
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from assistants.models.assistant import Assistant
from assistants.helpers.logging_helper import log_assistant_thought
from assistants.utils.thought_logger import log_symbolic_thought
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from intel_core.models import DocumentChunk, DocumentProgress
from intel_core.utils.document_progress import repair_progress


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def repair_documents(request, slug):
    """Repair linked documents and revalidate embeddings."""
    assistant = get_object_or_404(Assistant, slug=slug)
    results = []
    for doc in assistant.documents.all():
        repair_progress(document=doc)
        progress = DocumentProgress.objects.filter(document=doc).first()
        embedded = progress.embedded_chunks if progress else DocumentChunk.objects.filter(document=doc, embedding_status="embedded").count()
        total = progress.total_chunks if progress else DocumentChunk.objects.filter(document=doc).count()
        status = progress.status if progress else doc.status
        results.append({
            "document_id": str(doc.id),
            "title": doc.title,
            "embedded": embedded,
            "total": total,
            "status": status,
        })
    log_assistant_thought(assistant, f"Document repair run on {len(results)} docs", thought_type="reflection")
    log_symbolic_thought(
        assistant,
        category="repair",
        thought=f"Repaired {len(results)} documents",
        thought_type="repair",
        tool_name="repair_tool",
        tool_result_summary=f"{len(results)} docs",
        origin="auto-reflect",
    )
    return Response({"documents": results})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reflect_again(request, slug):
    """Trigger document reflection rerun for linked documents."""
    assistant = get_object_or_404(Assistant, slug=slug)
    doc_id = request.query_params.get("doc_id")
    docs = assistant.documents.all()
    if doc_id:
        docs = docs.filter(id=doc_id)
        if not docs.exists():
            return Response({"error": "Document not linked"}, status=404)
    engine = AssistantReflectionEngine(assistant)
    results = []
    for doc in docs:
        summary, _, _ = engine.reflect_on_document(doc)
        results.append({"document_id": str(doc.id), "summary": summary})
    log_assistant_thought(
        assistant,
        f"Reflect again on {len(results)} docs",
        thought_type="reflection",
    )
    task_id = str(uuid4())
    return Response({"results": results, "status": "complete", "task_id": task_id})
