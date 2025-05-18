# mcp_core/views/dev_docs.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from mcp_core.models import DevDoc, GroupedDevDocReflection
from mcp_core.serializers import DevDocSerializer, GroupedDevDocReflectionSerializer
from mcp_core.utils.devdoc_reflection import (
    reflect_on_devdoc,
    summarize_and_group_devdocs,
)
from django.shortcuts import get_object_or_404
from memory.models import MemoryEntry
import logging


logger = logging.getLogger("embeddings")


@api_view(["GET"])
def list_dev_docs(request):
    docs = DevDoc.objects.all().order_by("-created_at")
    serializer = DevDocSerializer(docs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_dev_doc(request, slug):
    doc = get_object_or_404(DevDoc, slug=slug)
    serializer = DevDocSerializer(doc)
    return Response(serializer.data)


@api_view(["POST"])
def reflect_on_devdoc_view(request, pk):
    try:
        doc = DevDoc.objects.get(pk=pk)
    except DevDoc.DoesNotExist:
        return Response({"error": "DevDoc not found"}, status=404)

    memory = reflect_on_devdoc(doc)
    return Response(
        {
            "memory_id": memory.id,
            "summary": memory.summary,
            "event": memory.event,
            "tags": [tag.name for tag in memory.tags.all()],
            "created_at": memory.created_at,
        }
    )


@api_view(["GET"])
def devdoc_reflection_by_slug(request, slug):
    try:
        doc = DevDoc.objects.get(slug=slug)
        memory = (
            MemoryEntry.objects.filter(document=doc).order_by("-created_at").first()
        )
        if not memory:
            return Response({"error": "No reflection found."}, status=404)

        return Response(
            {
                "memory_id": memory.id,
                "summary": memory.summary,
                "event": memory.event,
                "tags": [tag.name for tag in memory.tags.all()],
                "created_at": memory.created_at,
            }
        )
    except DevDoc.DoesNotExist:
        return Response({"error": "DevDoc not found."}, status=404)


@api_view(["GET", "POST"])
def devdoc_detail(request, slug):
    doc = DevDoc.objects.get(slug=slug)
    return Response(
        {
            "id": doc.id,  # <- ADD THIS
            "slug": doc.slug,
            "title": doc.title,
            "content": doc.content,
        }
    )


@api_view(["POST"])
def summarize_and_group_devdocs_view(request):
    try:
        grouped = summarize_and_group_devdocs()
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    return Response(
        {
            "summary": grouped.summary,
            "event": grouped.raw_json,
            "tags": [t.name for t in grouped.tags.all()],
            "created_at": grouped.created_at,
            "reflection_id": grouped.id,
        }
    )


@api_view(["GET"])
def grouped_reflection_history(request):
    reflections = GroupedDevDocReflection.objects.order_by("-created_at")[:10]
    serializer = GroupedDevDocReflectionSerializer(reflections, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def grouped_reflection_detail(request, pk):
    try:
        reflection = GroupedDevDocReflection.objects.get(id=pk)
    except GroupedDevDocReflection.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    serializer = GroupedDevDocReflectionSerializer(reflection)
    return Response(serializer.data)
