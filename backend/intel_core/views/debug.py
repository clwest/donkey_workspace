from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from intel_core.models import Document, DocumentChunk
import os
from intel_core.management.commands.fix_doc_progress import Command as FixCommand
from embeddings.document_services.chunking import clean_and_score_chunk
from utils.logging_utils import get_logger

logger = get_logger(__name__)


def repair_progress(document=None, document_id=None):
    """Repair DocumentProgress records for a single document."""
    from intel_core.models import Document

    if document == "all" or document_id == "all":
        logger.warning(
            "\u26d4\ufe0f Invalid use of 'all' in repair_progress \u2014 this is only supported via CLI."
        )
        return None

    try:
        if document_id:
            document = Document.objects.get(id=document_id)
        elif not document:
            logger.warning(
                "\u26a0\ufe0f repair_progress called without a valid document or document_id."
            )
            return None
    except Document.DoesNotExist:
        logger.warning(f"\u274c Document not found for repair: {document_id}")
        return None

    cmd = FixCommand()
    cmd.stdout = open(os.devnull, "w")
    cmd.stderr = open(os.devnull, "w")
    logger.info(f"🔧 Repairing document progress for: {document.title}")
    return cmd.handle(doc_id=str(document.id), repair=True)


@api_view(["GET"])
def debug_doc_chunks(request, doc_id):
    chunks = DocumentChunk.objects.filter(document_id=doc_id).order_by("order")
    out = [
        {
            "id": str(c.id),
            "order": c.order,
            "tokens": c.tokens,
            "score": c.score,
            "glossary_score": c.glossary_score,
            "matched_anchors": c.matched_anchors,
            "fingerprint": c.fingerprint,
            "text_preview": c.text[:300],
        }
        for c in chunks
    ]
    return Response(out)


@api_view(["GET"])
def rag_recall(request):
    query = request.query_params.get("query", "")
    assistant = request.query_params.get("assistant")
    from assistants.utils.chunk_retriever import get_relevant_chunks

    (
        chunks,
        reason,
        fallback,
        glossary_present,
        top_score,
        _,
        glossary_forced,
        _,
        _,
        debug_info,
    ) = get_relevant_chunks(assistant, query)
    forced_chunks = [c["chunk_id"] for c in chunks if c.get("forced_included")]
    debug = {
        "reason": reason,
        "fallback": fallback,
        "glossary_present": glossary_present,
        "top_score": top_score,
        "glossary_forced": glossary_forced,
        "forced_chunks": forced_chunks,
        **debug_info,
    }
    return Response({"results": chunks, "debug": debug})


@api_view(["POST", "GET"])
def recalc_scores(request):
    """Recalculate chunk relevance scores for a document."""
    doc_id = request.data.get("document_id") or request.query_params.get("doc_id")
    if not doc_id:
        return Response(
            {"error": "document_id required"}, status=status.HTTP_400_BAD_REQUEST
        )

    document = Document.objects.filter(id=doc_id).first()
    if not document:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    chunks = DocumentChunk.objects.filter(document=document).order_by("order")
    updated = 0
    for chunk in chunks:
        info = clean_and_score_chunk(chunk.text, chunk_index=chunk.order)
        chunk.score = info.get("score", 0.0)
        chunk.save(update_fields=["score"])
        updated += 1

    return Response({"updated": updated})


@api_view(["GET"])
def verify_embeddings(request):
    """Return mismatched chunks for a document."""
    doc_id = request.query_params.get("document_id")
    recalc = request.query_params.get("recalculate") == "true"
    if not doc_id:
        return Response(
            {"error": "document_id required"}, status=status.HTTP_400_BAD_REQUEST
        )

    document = Document.objects.filter(id=doc_id).first()
    if not document:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    chunks = DocumentChunk.objects.filter(document=document).order_by("order")
    mismatches = []
    for ch in chunks:
        emb_id = getattr(ch.embedding, "embedding_id", None)
        if ch.embedding_status == "embedded":
            if not emb_id:
                mismatches.append({"id": str(ch.id), "issue": "missing embedding"})
        else:
            mismatches.append(
                {"id": str(ch.id), "issue": f"status={ch.embedding_status}"}
            )
            if recalc:
                ch.embedding_status = "pending"
                ch.save(update_fields=["embedding_status"])
                from embeddings.tasks import embed_and_store

                embed_and_store.delay(str(ch.id))

    return Response({"mismatches": mismatches})


@api_view(["POST"])
def repair_progress_view(request):
    """Run fix_doc_progress logic for a document and return summary."""
    doc_id = request.data.get("doc_id") or request.query_params.get("doc_id")
    if not doc_id:
        return Response({"error": "Missing doc_id"}, status=400)

    result = repair_progress(document_id=doc_id)
    return Response({"status": "repaired", "details": result})


@api_view(["POST"])
def fix_embeddings(request):
    """Correct embedding_status based on EmbeddingMetadata."""
    doc_id = request.data.get("doc_id") or request.query_params.get("doc_id")
    if not doc_id:
        return Response({"error": "Missing doc_id"}, status=400)

    chunks = DocumentChunk.objects.filter(
        document_id=doc_id, embedding__status="completed"
    ).exclude(embedding_status="embedded")
    updated = 0
    for ch in chunks:
        ch.embedding_status = "embedded"
        ch.save(update_fields=["embedding_status"])
        updated += 1
    return Response({"updated": updated})


@api_view(["POST"])
def sync_chunk_counts_view(request):
    """Synchronize DocumentProgress.total_chunks with actual chunk counts."""
    from io import StringIO
    from intel_core.management.commands.sync_chunk_counts import Command as SyncCommand

    buf = StringIO()
    cmd = SyncCommand()
    cmd.stdout = buf
    cmd.stderr = buf
    cmd.handle()
    return Response({"detail": buf.getvalue().strip()})
