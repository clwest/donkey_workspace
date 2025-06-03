from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import json
import uuid
import os
from django.core.files.storage import default_storage
from django.conf import settings
from intel_core.services import DocumentService
from intel_core.models import (
    Document,
    DocumentFavorite,
    DocumentProgress,
    DocumentSet,
    JobStatus,
)
from intel_core.serializers import DocumentSerializer, DocumentSetSerializer
from intel_core.tasks import create_document_set_task
from prompts.utils.token_helpers import count_tokens, smart_chunk_prompt
from assistants.models.assistant import Assistant


@api_view(["GET"])
@permission_classes([AllowAny])
def list_documents(request):
    """Return distinct documents for linking."""

    docs = Document.objects.order_by(
        "title",
        "source_type",
        "source_url",
        "-created_at",
    ).distinct("title", "source_type", "source_url")

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


@api_view(["GET", "DELETE"])
@permission_classes([AllowAny])
def document_detail_view(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "DELETE":
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    chunks = document.chunks.order_by("order")
    chunk_data = [
        {
            "id": str(chunk.id),
            "order": chunk.order,
            "tokens": chunk.tokens,
            "score": chunk.score,
            "quality_notes": chunk.quality_notes,
            "chunk_type": chunk.chunk_type,
            "is_glossary": chunk.is_glossary,
            "tags": chunk.tags,
            "embedding_status": chunk.embedding_status,
            "text": chunk.text,
        }
        for chunk in chunks
    ]

    smart_chunks = smart_chunk_prompt(document.content)

    chunk_count = chunks.count()
    num_embedded = chunks.filter(embedding__isnull=False).count()
    if num_embedded == 0:
        embed_status = "pending"
    elif num_embedded == chunk_count:
        embed_status = "completed"
    else:
        embed_status = "partial"
    glossary_ids = list(chunks.filter(is_glossary=True).values_list("id", flat=True))

    token_count = document.token_count_int or document.metadata.get("token_count") or count_tokens(document.content)

    data = {
        "id": str(document.id),
        "title": document.title,
        "source_url": document.source_url,
        "source_type": document.source_type,
        "description": document.description,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
        "metadata": document.metadata,
        "token_count": token_count,
        "chunk_count": chunk_count,
        "embedded_chunks": num_embedded,
        "embedding_status": {
            "embedded": num_embedded,
            "total": chunk_count,
            "status": embed_status,
        },
        "glossary_ids": [str(g) for g in glossary_ids],
        "content": document.content,
        "chunks": chunk_data,
        "smart_chunks": smart_chunks,
        "summary": document.summary,
        "assistants": [
            {
                "id": str(a.id),
                "slug": a.slug,
                "name": a.name,
            }
            for a in document.linked_assistants.all()
        ],
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


@api_view(["POST"])
@permission_classes([AllowAny])
def create_document_set(request):
    """Create a DocumentSet from uploaded sources."""
    title = request.data.get("title") or "Untitled"
    urls = request.data.get("urls") or []
    videos = request.data.get("videos") or []
    tags = request.data.get("tags") or []
    files = request.FILES.getlist("files")

    if isinstance(urls, str):
        try:
            urls = json.loads(urls)
        except Exception:
            urls = [u.strip() for u in urls.split(",") if u.strip()]
    if isinstance(videos, str):
        try:
            videos = json.loads(videos)
        except Exception:
            videos = [v.strip() for v in videos.split(",") if v.strip()]
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = [t.strip() for t in tags.split(",") if t.strip()]

    session_id = request.data.get("session_id") or str(uuid.uuid4())
    job = JobStatus.objects.create(status="queued", session_id=session_id)

    file_paths = []
    for f in files:
        path = default_storage.save(f.name, f)
        file_paths.append(os.path.join(settings.MEDIA_ROOT, path))

    create_document_set_task.delay(
        title=title,
        urls=urls,
        videos=videos,
        file_paths=file_paths,
        tags=tags,
        session_id=session_id,
        job_id=str(job.job_id),
    )

    return Response({"session_id": session_id}, status=202)


@api_view(["GET"])
@permission_classes([AllowAny])
def document_set_detail(request, pk):
    try:
        ds = DocumentSet.objects.get(pk=pk)
    except DocumentSet.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    return Response(DocumentSetSerializer(ds).data)
