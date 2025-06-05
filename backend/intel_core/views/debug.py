from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from intel_core.models import Document, DocumentChunk
from embeddings.document_services.chunking import clean_and_score_chunk
from utils.logging_utils import get_logger
from intel_core.utils.embedding_debug import reembed_missing_chunks
from intel_core.utils.document_progress import repair_progress

logger = get_logger(__name__)



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


@api_view(["POST"])
def reembed_missing_chunks_view(request):
    """Trigger reembedding for chunks missing vectors or scores."""
    report = reembed_missing_chunks()
    return Response(report)


@api_view(["POST"])
def boost_glossary_term(request):
    """Boost retrieval weight for a raw term and reembed related chunks."""
    term = request.data.get("term")
    if not term:
        return Response({"error": "term required"}, status=400)
    boost = float(request.data.get("boost", 0.1))
    from django.utils.text import slugify
    from memory.models import SymbolicMemoryAnchor, GlossaryChangeEvent
    from embeddings.tasks import embed_and_store

    slug = slugify(term)
    anchor, _ = SymbolicMemoryAnchor.objects.get_or_create(
        slug=slug, defaults={"label": term}
    )
    chunks = DocumentChunk.objects.filter(text__icontains=term)
    updated = 0
    for ch in chunks:
        ch.anchor = anchor
        ch.glossary_boost = boost
        ch.save(update_fields=["anchor", "glossary_boost"])
        embed_and_store.delay(str(ch.id))
        updated += 1
    GlossaryChangeEvent.objects.create(
        term=term, boost=boost, created_by=request.user if request.user.is_authenticated else None
    )
    return Response({"updated": updated, "term": term, "boost": boost})


@api_view(["POST"])
def suggest_glossary_anchor(request):
    """Suggest a new glossary anchor term."""
    term = request.data.get("term")
    if not term:
        return Response({"error": "term required"}, status=400)
    from django.utils.text import slugify
    from memory.models import SymbolicMemoryAnchor, GlossaryChangeEvent

    anchor, _ = SymbolicMemoryAnchor.objects.get_or_create(
        slug=slugify(term), defaults={"label": term}
    )
    GlossaryChangeEvent.objects.create(
        term=term, boost=0.0, created_by=request.user if request.user.is_authenticated else None
    )
    return Response({"anchor": anchor.slug})
