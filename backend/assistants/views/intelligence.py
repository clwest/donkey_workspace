from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from assistants.models.project import AssistantProject
from intel_core.models import Document
from mcp_core.models import NarrativeThread
from assistants.serializers import AssistantNextActionSerializer
from assistants.utils.assistant_reflection_engine import plan_from_thread_context
from assistants.utils.core_assistant import CoreAssistant


@api_view(["POST"])
@permission_classes([AllowAny])
def plan_from_thread(request, slug):
    """Generate next actions for a narrative thread."""
    assistant = get_object_or_404(Assistant, slug=slug)
    thread_id = request.data.get("thread_id")
    if not thread_id:
        return Response({"error": "thread_id required"}, status=400)
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    project = None
    project_id = request.data.get("project_id")
    if project_id:
        project = get_object_or_404(AssistantProject, id=project_id)

    actions = plan_from_thread_context(thread, assistant, project)
    serializer = AssistantNextActionSerializer(actions, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def run_task(request, slug):
    """Execute a natural language task with the assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    task = request.data.get("task")
    if not task:
        return Response({"error": "task required"}, status=400)
    engine = CoreAssistant(assistant)
    result = engine.run_task(task)
    return Response(result)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_docs(request, slug):
    """Search documents linked to an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response({"error": "q required"}, status=400)

    docs = Document.objects.filter(linked_assistants=assistant)
    if assistant.document_set:
        docs = docs | assistant.document_set.documents.all()
    docs = docs.distinct()

    q_lower = query.lower()
    results = []
    for doc in docs:
        title = doc.title or ""
        content = doc.content or ""
        if q_lower in title.lower() or q_lower in content.lower():
            idx = content.lower().find(q_lower)
            snippet = content[max(idx - 50, 0) : idx + 150] if idx != -1 else content[:200]
            results.append(
                {
                    "id": str(doc.id),
                    "title": doc.title,
                    "preview": snippet.strip(),
                    "source_url": doc.source_url,
                    "score": 1.0,
                }
            )
    return Response(results)
