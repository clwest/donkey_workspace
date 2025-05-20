from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.conf import settings
import os
import json
from openai import OpenAI
from django.contrib.auth import get_user_model
from intel_core.models import Document
from assistants.models import Assistant, AssistantProject, AssistantObjective
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread, Tag
from prompts.models import Prompt
from prompts.utils.token_helpers import count_tokens
from intel_core.serializers import DocumentSerializer
from intel_core.processors.url_loader import load_urls
from intel_core.processors.video_loader import load_videos
from intel_core.processors.pdf_loader import load_pdfs

client = OpenAI()
User = get_user_model()


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def unified_ingestion_view(request):
    """
    Accepts YouTube URLs, web URLs, or PDF uploads and ingests them into the system.
    """
    source_type = request.data.get("source_type")  # "youtube", "pdf", or "url"
    project_name = request.data.get("project_name", "General")
    session_id = request.data.get("session_id")
    user_provided_title = request.data.get("title")

    try:
        if source_type == "youtube":
            video_urls = request.data.get("urls")
            documents = load_videos(
                video_urls, user_provided_title, project_name, session_id
            )
            serialized = [
                DocumentSerializer(doc).data
                for doc in documents
                if isinstance(doc, Document)
            ]
            return Response({"documents": serialized})

        elif source_type == "url":
            urls = request.data.get("urls", [])
            if isinstance(urls, str):
                urls = [urls]
            tag_names = request.data.get("tags", [])
            if isinstance(tag_names, str):
                try:
                    tag_names = json.loads(tag_names)
                except Exception:
                    tag_names = [t.strip() for t in tag_names.split(",") if t.strip()]

            tags = []
            for tag_name in tag_names:
                if tag_name and str(tag_name).strip():
                    cleaned = str(tag_name).strip().lower()
                    tag, _ = Tag.objects.get_or_create(name=cleaned)
                    tags.append(tag)

            docs = load_urls(urls, user_provided_title, project_name, session_id)
            for doc in docs:
                doc.tags.set(tags)

            serialized = [
                DocumentSerializer(doc).data
                for doc in docs
                if isinstance(doc, Document)
            ]
            return Response(
                {
                    "documents": serialized,
                    "message": f"Loaded {len(serialized)} URL document(s).",
                }
            )

        elif source_type == "pdf":
            uploaded_files = request.FILES.getlist("files")
            if not uploaded_files:
                return Response({"error": "No PDF files provided."}, status=400)

            file_paths = []
            for f in uploaded_files:
                path = default_storage.save(f"temp/{f.name}", f)
                file_paths.append(os.path.join(settings.MEDIA_ROOT, path))

            documents = load_pdfs(
                file_paths, user_provided_title, project_name, session_id
            )
            serialized = [
                DocumentSerializer(doc).data
                for doc in documents
                if isinstance(doc, Document)
            ]
            return Response({"documents": serialized})

        return Response({"error": "Invalid or missing source_type"}, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
