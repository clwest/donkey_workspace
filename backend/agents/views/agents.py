from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from agents.models import Agent, AgentFeedbackLog, AgentCluster, SwarmMemoryEntry
from agents.serializers import AgentSerializer, AgentFeedbackLogSerializer, AgentClusterSerializer
from agents.serializers import SwarmMemoryEntrySerializer
from agents.utils.agent_controller import (
    update_agent_profile_from_feedback,
    train_agent_from_documents,
    recommend_training_documents,
    retire_agent,
)
from agents.utils.swarm_analytics import generate_temporal_swarm_report, get_swarm_snapshot
from datetime import datetime

@api_view(["GET"])
def list_agents(request):
    agents = Agent.objects.all().order_by("created_at")
    serializer = AgentSerializer(agents, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def agent_detail_view(request, slug):
    try:
        agent = Agent.objects.get(slug=slug)
    except Agent.DoesNotExist:
        return Response({"error": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AgentSerializer(agent)
    return Response(serializer.data)


@api_view(["GET"])
def agent_feedback_logs(request, id):
    agent = get_object_or_404(Agent, id=id)
    logs = AgentFeedbackLog.objects.filter(agent=agent).order_by("-created_at")
    serializer = AgentFeedbackLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def update_agent_from_feedback(request, id):
    agent = get_object_or_404(Agent, id=id)
    records = request.data.get("feedback", [])
    if not isinstance(records, list):
        return Response({"error": "feedback must be a list"}, status=400)
    logs = []
    for item in records:
        log = AgentFeedbackLog.objects.create(
            agent=agent,
            task_id=item.get("task"),
            feedback_text=item.get("feedback_text", ""),
            feedback_type=item.get("feedback_type", "reflection"),
            score=item.get("score"),
        )
        logs.append(log)

    summary = update_agent_profile_from_feedback(agent, logs)
    return Response({"updated": True, "summary": summary})


@api_view(["POST"])
def train_agent(request, id):
    agent = get_object_or_404(Agent, id=id)
    doc_ids = request.data.get("document_ids", [])
    if not isinstance(doc_ids, list):
        return Response({"error": "document_ids must be a list"}, status=400)
    from intel_core.models import Document

    docs = Document.objects.filter(id__in=doc_ids)
    result = train_agent_from_documents(agent, list(docs))
    serializer = AgentSerializer(agent)
    return Response({"agent": serializer.data, "result": result})


@api_view(["GET"])
def recommend_training_docs(request, id):
    agent = get_object_or_404(Agent, id=id)
    docs = recommend_training_documents(agent)
    from intel_core.serializers import DocumentSerializer

    data = DocumentSerializer(docs, many=True).data
    return Response(data)

@api_view(["GET"])
def list_clusters(request):
    clusters = AgentCluster.objects.all().order_by("-created_at")
    serializer = AgentClusterSerializer(clusters, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def cluster_detail_view(request, id):
    cluster = get_object_or_404(AgentCluster, id=id)
    serializer = AgentClusterSerializer(cluster)
    return Response(serializer.data)


@api_view(["GET"])
def swarm_temporal_report(request):
    data = generate_temporal_swarm_report()
    return Response(data)


@api_view(["GET"])
def swarm_memory(request):
    tag = request.query_params.get("tag")
    qs = SwarmMemoryEntry.objects.all().order_by("-created_at")
    if tag:
        qs = qs.filter(tags__name__iexact=tag)
    serializer = SwarmMemoryEntrySerializer(qs[:50], many=True)
    return Response(serializer.data)


@api_view(["GET"])
def swarm_snapshot_view(request, date):
    try:
        dt = datetime.fromisoformat(date)
    except ValueError:
        return Response({"error": "Invalid date"}, status=400)
    snapshot = get_swarm_snapshot(dt)
    return Response({
        "agents": AgentSerializer(snapshot["agents"], many=True).data,
        "clusters": AgentClusterSerializer(snapshot["clusters"], many=True).data,
        "memories": SwarmMemoryEntrySerializer(snapshot["memories"], many=True).data,
    })


@api_view(["POST"])
def retire_agents(request):
    reason = request.data.get("reason", "No reason provided")
    retired = []
    for agent in Agent.objects.filter(is_active=True)[:1]:
        entry = retire_agent(agent, reason)
        retired.append(entry.id)
    return Response({"retired": retired})
