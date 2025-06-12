from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from agents.models.core import Agent, TrainedAgentLog
from intel_core.models import Document
from assistants.serializers_pass import AssistantSerializer
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


@api_view(["POST"])
def promote_trained_agent(request):
    log_id = request.data.get("log_id")
    if not log_id:
        return Response({"error": "log_id required"}, status=400)

    log = get_object_or_404(TrainedAgentLog, id=log_id)
    agent = log.agent

    assistant = Assistant.objects.create(
        name=log.label,
        description=agent.description,
        specialty=agent.specialty,
        system_prompt=log.prompt,
        document_set=log.document_set,
        traits=list(agent.skills or []),
    )
    if log.document_set:
        assistant.documents.set(log.document_set.documents.all())

    serializer = AssistantSerializer(assistant)
    return Response(serializer.data, status=201)
