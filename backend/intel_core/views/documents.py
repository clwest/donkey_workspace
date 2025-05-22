from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from intel_core.models import Document, DocumentFavorite, DocumentProgress
from intel_core.serializers import DocumentSerializer
from prompts.utils.token_helpers import count_tokens, smart_chunk_prompt
from assistants.models.assistant import Assistant


@api_view(["GET"])
@permission_classes([AllowAny])
def list_documents(request):
    """Return distinct documents for linking."""

    docs = (
        Document.objects.order_by(
            "title",
            "source_type",
            "source_url",
            "-created_at",
        ).distinct("title", "source_type", "source_url")
    )

    assistant_slug = request.query_params.get("exclude_for")
    if assistant_slug:
        try:
            assistant = Assistant.objects.get(slug=assistant_slug)
            docs = docs.exclude(linked_assistants=assistant)
        except Assistant.DoesNotExist:
            pass


    limit = int(request.query_params.get("limit", 50))
    docs = docs[:limit]

    serializer = DocumentSerializer(docs, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def document_detail_view(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    chunks = document.chunks.order_by("order")
    chunk_data = [
        {
            "id": str(chunk.id),
            "order": chunk.order,
            "tokens": chunk.tokens,
            "chunk_type": chunk.chunk_type,
            "text": chunk.text,
        }
        for chunk in chunks
    ]

    smart_chunks = smart_chunk_prompt(document.content)

    data = {
        "id": str(document.id),
        "title": document.title,
        "source_url": document.source_url,
        "source_type": document.source_type,
        "description": document.description,
        "created_at": document.created_at,
        "metadata": document.metadata,
        "total_tokens": count_tokens(document.content),
        "content": document.content,
        "chunks": chunk_data,
        "smart_chunks": smart_chunks,
        "summary": document.summary,
    }

    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def toggle_favorite(request, pk):
    try:
        doc = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response({"error": "Document not found"}, status=404)

    user = (
        request.user
        if request.user.is_authenticated
        else get_user_model().objects.first()
    )

    if not user:
        return Response({"error": "No user available to assign favorite"}, status=403)

    favorite, created = DocumentFavorite.objects.get_or_create(
        user=user,
        document=doc,
    )

    if not created:
        favorite.delete()
        return Response({"favorited": False})

    return Response({"favorited": True})


# intel_core/views/documents.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Sum, Count, Max
from intel_core.models import Document
from intel_core.serializers import DocumentSerializer
from django.db.models import Count, IntegerField, Sum, Value
from django.db.models.functions import Cast, Coalesce
from django.db.models.expressions import RawSQL


@api_view(["GET"])
@permission_classes([AllowAny])
def list_grouped_documents(request):
    # Step 1: Group by title + source_type + source_url
    grouped = (
        Document.objects.annotate(
            token_count_casted=Cast(
                RawSQL("(metadata->>'token_count')::int", ()), IntegerField()
            )
        )
        .values("title", "source_type", "source_url")
        .annotate(
            total_tokens=Coalesce(Sum("token_count_casted"), 0),
            document_count=Count("id"),
            latest_created_at=Max("created_at"),
        )
        .order_by("-latest_created_at")
    )

    # Step 2: Attach matching documents to each group
    results = []
    for group in grouped:
        docs = Document.objects.filter(
            title=group["title"],
            source_type=group["source_type"],
            source_url=group["source_url"],
        ).order_by("created_at")

        serialized_docs = DocumentSerializer(docs, many=True).data

        results.append(
            {
                "title": group["title"],
                "source_type": group["source_type"],
                "source_url": group["source_url"],
                "total_tokens": group["total_tokens"],
                "document_count": group["document_count"],
                "latest_created": group["latest_created_at"],
                "documents": serialized_docs,
            }
        )

    return Response(results)


@api_view(["GET"])
@permission_classes([AllowAny])
def document_progress_view(request, pk):
    """Return chunking progress for a document group."""
    try:
        progress = DocumentProgress.objects.get(progress_id=pk)
    except DocumentProgress.DoesNotExist:
        return Response({"error": "Progress not found"}, status=404)

    data = {
        "document_id": str(progress.progress_id),
        "title": progress.title,
        "total_chunks": progress.total_chunks,
        "processed": progress.processed,
        "failed_chunks": progress.failed_chunks,
        "status": progress.status,
    }
    return Response(data)
