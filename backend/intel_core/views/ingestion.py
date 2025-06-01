from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response

from intel_core.serializers import DocumentSerializer
from intel_core.services import DocumentService
import json


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
    assistant_id = request.data.get("assistant_id")
    if not assistant_id:
        return Response({"error": "assistant_id required"}, status=400)
    project_id = request.data.get("project_id")
    reflect_after = str(request.data.get("reflect_after", "false")).lower() in [
        "1",
        "true",
        "yes",
    ]

    urls = request.data.get("urls")
    if isinstance(urls, str):
        urls = [urls]

    tag_names = request.data.get("tags", [])
    if isinstance(tag_names, str):
        try:
            tag_names = json.loads(tag_names)
        except Exception:
            tag_names = [t.strip() for t in tag_names.split(",") if t.strip()]

    uploaded_files = request.FILES.getlist("files")

    try:
        docs = DocumentService.ingest(
            source_type=source_type,
            urls=urls,
            files=uploaded_files,
            title=user_provided_title,
            project_name=project_name,
            session_id=session_id,
            assistant_id=assistant_id,
            project_id=project_id,
            tags=tag_names,
        )

        if reflect_after and docs:
            from assistants.utils.assistant_reflection_engine import (
                AssistantReflectionEngine,
            )
            from assistants.models import Assistant

            assistant = Assistant.objects.filter(id=assistant_id).first()
            if not assistant:
                assistant = Assistant.objects.filter(slug=assistant_id).first()
            if assistant:
                engine = AssistantReflectionEngine(assistant)
                for doc in docs:
                    try:
                        engine.reflect_on_document(doc)
                    except Exception:
                        pass

        serialized = [DocumentSerializer(doc).data for doc in docs]

        response = {"documents": serialized}
        if source_type == "url":
            response["message"] = f"Loaded {len(serialized)} URL document(s)."
        return Response(response)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
