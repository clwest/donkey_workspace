from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from agents.models import (
    Agent,
    AgentFeedbackLog,
    AgentCluster,
    SwarmMemoryEntry,
    LoreEpoch,
    LoreEntry,
    RetconRequest,
    RealityConsensusVote,
    MythDiplomacySession,
    RitualCollapseLog,
    LegacyArtifact,
    ReincarnationLog,
    ReturnCycle,
    LoreToken,
)
from agents.serializers import (
    AgentSerializer,
    AgentFeedbackLogSerializer,
    AgentClusterSerializer,
    SwarmMemoryEntrySerializer,
    LoreEntrySerializer,
    LoreEpochSerializer,
    RetconRequestSerializer,
    RealityConsensusVoteSerializer,
    MythDiplomacySessionSerializer,
    RitualCollapseLogSerializer,
    LegacyArtifactSerializer,
    ReincarnationLogSerializer,
    ReturnCycleSerializer,
    LoreTokenSerializer,
)
from assistants.serializers import AssistantCivilizationSerializer

from agents.utils.agent_controller import (
    update_agent_profile_from_feedback,
    train_agent_from_documents,
    recommend_training_documents,
    retire_agent,
)
from agents.utils.lore_token import compress_memories_to_token

from agents.utils.swarm_analytics import (
    generate_temporal_swarm_report,
    get_swarm_snapshot,
)

from agents.utils import harmonize_global_narrative

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
def create_agent_feedback(request, id):
    agent = get_object_or_404(Agent, id=id)
    serializer = AgentFeedbackLogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(agent=agent)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


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
    return Response(
        {
            "agents": AgentSerializer(snapshot["agents"], many=True).data,
            "clusters": AgentClusterSerializer(snapshot["clusters"], many=True).data,
            "memories": SwarmMemoryEntrySerializer(
                snapshot["memories"], many=True
            ).data,
        }
    )


@api_view(["GET"])
def list_treaties(request):
    """Return active diplomacy treaties."""
    sessions = MythDiplomacySession.objects.all().order_by("-created_at")
    data = []
    for session in sessions:
        participants = [c.name for c in session.factions.all()]
        data.append(
            {
                "id": session.id,
                "name": session.topic,
                "participants": participants,
                "status": session.status,
            }
        )
    return Response(data)


@api_view(["POST"])
def retire_agents(request):
    reason = request.data.get("reason", "No reason provided")
    retired = []
    for agent in Agent.objects.filter(is_active=True)[:1]:
        entry = retire_agent(agent, reason)
        retired.append(entry.id)
    return Response({"retired": retired})


@api_view(["GET", "POST"])
def lore_entries(request):
    if request.method == "GET":
        entries = LoreEntry.objects.all().order_by("-created_at")
        return Response(LoreEntrySerializer(entries, many=True).data)

    serializer = LoreEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    entry = serializer.save()
    return Response(LoreEntrySerializer(entry).data, status=201)


@api_view(["GET", "POST"])
def retcon_requests(request):
    if request.method == "GET":
        requests = RetconRequest.objects.all().order_by("-created_at")
        return Response(RetconRequestSerializer(requests, many=True).data)

    serializer = RetconRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    req = serializer.save()
    return Response(RetconRequestSerializer(req).data, status=201)


@api_view(["GET", "POST"])
def lore_epochs(request):
    """List or create lore epochs."""
    if request.method == "GET":
        epochs = LoreEpoch.objects.all().order_by("-created_at")
        return Response(LoreEpochSerializer(epochs, many=True).data)

    serializer = LoreEpochSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    epoch = serializer.save()
    return Response(LoreEpochSerializer(epoch).data, status=201)


@api_view(["POST"])
def myth_reset_cycle(request):
    result = run_myth_reset_cycle()
    return Response(result)


@api_view(["GET"])
def assistant_civilizations(request):
    from assistants.models import AssistantCivilization

    civs = AssistantCivilization.objects.all().order_by("-created_at")
    serializer = AssistantCivilizationSerializer(civs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def consensus_votes(request):
    votes = RealityConsensusVote.objects.all().order_by("-created_at")
    serializer = RealityConsensusVoteSerializer(votes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def myth_diplomacy_sessions(request):
    sessions = MythDiplomacySession.objects.all().order_by("-created_at")
    serializer = MythDiplomacySessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def ritual_collapse_logs(request):
    logs = RitualCollapseLog.objects.all().order_by("-created_at")
    serializer = RitualCollapseLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def belief_clusters(request):
    from assistants.utils.belief_clustering import cluster_assistant_beliefs

    data = cluster_assistant_beliefs()
    return Response(data)


@api_view(["GET"])
def lore_inheritance_lines(request):
    """Placeholder for lore inheritance data."""
    return Response([])


@api_view(["GET"])
def myth_simulation_arenas(request):
    """Placeholder for myth simulation arena data."""
    return Response([])


@api_view(["GET"])
def harmonize_global(request):
    data = harmonize_global_narrative()
    return Response(data)


@api_view(["GET", "POST"])
def artifacts(request):
    if request.method == "GET":
        items = LegacyArtifact.objects.all().order_by("-created_at")
        return Response(LegacyArtifactSerializer(items, many=True).data)

    serializer = LegacyArtifactSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    artifact = serializer.save()
    return Response(LegacyArtifactSerializer(artifact).data, status=201)


@api_view(["GET", "POST"])
def reincarnations(request):
    if request.method == "GET":
        logs = ReincarnationLog.objects.all().order_by("-created_at")
        return Response(ReincarnationLogSerializer(logs, many=True).data)

    serializer = ReincarnationLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log = serializer.save()
    return Response(ReincarnationLogSerializer(log).data, status=201)


@api_view(["GET", "POST"])
def return_cycles(request):
    if request.method == "GET":
        cycles = ReturnCycle.objects.all().order_by("-created_at")
        return Response(ReturnCycleSerializer(cycles, many=True).data)

    serializer = ReturnCycleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cycle = serializer.save()
    return Response(ReturnCycleSerializer(cycle).data, status=201)

@api_view(["GET", "POST"])
def lore_tokens(request):
    if request.method == "GET":
        tokens = LoreToken.objects.all().order_by("-created_at")
        return Response(LoreTokenSerializer(tokens, many=True).data)

    memory_ids = request.data.get("memory_ids", [])
    assistant_id = request.data.get("assistant")
    if not assistant_id:
        return Response({"error": "assistant required"}, status=400)
    assistant = get_object_or_404(Assistant, id=assistant_id)
    memories = list(SwarmMemoryEntry.objects.filter(id__in=memory_ids))
    token = compress_memories_to_token(memories, assistant)
    serializer = LoreTokenSerializer(token)
    return Response(serializer.data, status=201)
