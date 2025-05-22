from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from agents.models.core import Agent
from intel_core.models import Document
from assistants.utils.assistant_reflection_engine import (
    assign_training_documents,
    evaluate_agent_training,
)


@api_view(["POST"])
def assign_training(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    agent_id = request.data.get("agent_id")
    doc_ids = request.data.get("document_ids", [])
    if not agent_id or not doc_ids:
        return Response({"error": "agent_id and document_ids required"}, status=400)

    agent = get_object_or_404(Agent, id=agent_id)
    docs = list(Document.objects.filter(id__in=doc_ids))
    assignments = assign_training_documents(assistant, agent, docs)
    return Response({"assigned": [str(a.id) for a in assignments]})


@api_view(["GET"])
def evaluate_agent(request, slug, agent_id):
    assistant = get_object_or_404(Assistant, slug=slug)
    agent = get_object_or_404(Agent, id=agent_id)
    report = evaluate_agent_training(assistant, agent)
    return Response(report)
