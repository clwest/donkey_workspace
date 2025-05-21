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
    BeliefForkEvent,
    MythCollapseLog,
    MemoryReformationRitual,
    LegacyArtifact,
    ReincarnationLog,
    ReturnCycle,
    LoreToken,
    LoreTokenExchange,
    TokenMarket,
    LoreTokenCraftingRitual,
    LoreTokenSignature,
    TokenGuildVote,
    MythRegistryEntry,
    TemporalLoreAnchor,
    RitualComplianceRecord,
    EpistemologyNode,
    BeliefEntanglementLink,
    CognitiveConstraintProfile,
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
    LoreTokenCraftingRitualSerializer,
    LoreTokenSignatureSerializer,
    TokenGuildVoteSerializer,
    MythRegistryEntrySerializer,
    TemporalLoreAnchorSerializer,
    RitualComplianceRecordSerializer,
    BeliefForkEventSerializer,
    MythCollapseLogSerializer,
    MemoryReformationRitualSerializer,
    EpistemologyNodeSerializer,
    BeliefEntanglementLinkSerializer,
    CognitiveConstraintProfileSerializer,
)
from assistants.serializers import (
    AssistantCivilizationSerializer,
    AssistantReputationSerializer,
)
from assistants.models import Assistant, AssistantReputation

from agents.utils.agent_controller import (
    update_agent_profile_from_feedback,
    train_agent_from_documents,
    recommend_training_documents,
    retire_agent,
)
from agents.utils.lore_token import compress_memories_to_token, perform_token_ritual

from agents.utils.swarm_analytics import (
    generate_temporal_swarm_report,
    get_swarm_snapshot,
)

from agents.utils.myth_verification import (
    verify_lore_token_signature,
    sync_chronomyth_state,
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
        token_type = request.query_params.get("token_type")
        if token_type:
            tokens = tokens.filter(token_type=token_type)
        return Response(LoreTokenSerializer(tokens, many=True).data)

    memory_ids = request.data.get("memory_ids", [])
    assistant_id = request.data.get("assistant")
    if not assistant_id:
        return Response({"error": "assistant required"}, status=400)
    assistant = get_object_or_404(Assistant, id=assistant_id)
    memories = list(SwarmMemoryEntry.objects.filter(id__in=memory_ids))
    token_type = request.data.get("token_type", "insight")
    token = compress_memories_to_token(memories, assistant, token_type=token_type)
    serializer = LoreTokenSerializer(token)
    return Response(serializer.data, status=201)


@api_view(["GET", "POST"])
def lore_token_exchange(request):
    if request.method == "GET":
        exchanges = LoreTokenExchange.objects.all().order_by("-created_at")
        return Response(LoreTokenExchangeSerializer(exchanges, many=True).data)

    serializer = LoreTokenExchangeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    exchange = serializer.save()

    sender_rep, _ = AssistantReputation.objects.get_or_create(assistant=exchange.sender)
    sender_rep.tokens_endorsed += 1
    sender_rep.reputation_score = (
        sender_rep.tokens_created
        + sender_rep.tokens_endorsed
        + sender_rep.tokens_received
    )
    sender_rep.save()

    receiver_rep, _ = AssistantReputation.objects.get_or_create(
        assistant=exchange.receiver
    )
    receiver_rep.tokens_received += 1
    receiver_rep.reputation_score = (
        receiver_rep.tokens_created
        + receiver_rep.tokens_endorsed
        + receiver_rep.tokens_received
    )
    receiver_rep.save()

    return Response(LoreTokenExchangeSerializer(exchange).data, status=201)


@api_view(["GET", "POST"])
def token_market(request):
    if request.method == "GET":
        visibility = request.query_params.get("visibility")
        listings = TokenMarket.objects.all().order_by("-created_at")
        if visibility:
            listings = listings.filter(visibility=visibility)
        return Response(TokenMarketSerializer(listings, many=True).data)

    serializer = TokenMarketSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    listing = serializer.save()
    return Response(TokenMarketSerializer(listing).data, status=201)


@api_view(["GET", "POST"])
def token_rituals(request):
    if request.method == "GET":
        rituals = LoreTokenCraftingRitual.objects.all().order_by("-created_at")
        return Response(LoreTokenCraftingRitualSerializer(rituals, many=True).data)

    if request.data.get("complete"):
        ritual_id = request.data.get("ritual")
        ritual = get_object_or_404(LoreTokenCraftingRitual, id=ritual_id)
        token = perform_token_ritual(ritual)
        return Response(LoreTokenSerializer(token).data, status=201)

    serializer = LoreTokenCraftingRitualSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ritual = serializer.save()
    return Response(LoreTokenCraftingRitualSerializer(ritual).data, status=201)


@api_view(["GET", "POST"])
def token_votes(request):
    if request.method == "GET":
        votes = TokenGuildVote.objects.all().order_by("-created_at")
        return Response(TokenGuildVoteSerializer(votes, many=True).data)

    serializer = TokenGuildVoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    vote = serializer.save()
    return Response(TokenGuildVoteSerializer(vote).data, status=201)


@api_view(["GET", "POST"])
def myth_registry(request):
    if request.method == "GET":
        entries = MythRegistryEntry.objects.all().order_by("-created_at")
        return Response(MythRegistryEntrySerializer(entries, many=True).data)

    serializer = MythRegistryEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    entry = serializer.save()
    return Response(MythRegistryEntrySerializer(entry).data, status=201)


@api_view(["GET", "POST"])
def lore_anchors(request):
    if request.method == "GET":
        anchors = TemporalLoreAnchor.objects.all().order_by("-timestamp")
        return Response(TemporalLoreAnchorSerializer(anchors, many=True).data)

    serializer = TemporalLoreAnchorSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    anchor = serializer.save()
    return Response(TemporalLoreAnchorSerializer(anchor).data, status=201)


@api_view(["GET", "POST"])
def ritual_compliance(request):
    if request.method == "GET":
        records = RitualComplianceRecord.objects.all().order_by("-created_at")
        return Response(RitualComplianceRecordSerializer(records, many=True).data)

    serializer = RitualComplianceRecordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    record = serializer.save()
    return Response(RitualComplianceRecordSerializer(record).data, status=201)


@api_view(["GET", "POST"])
def token_signatures(request):
    if request.method == "GET":
        sigs = LoreTokenSignature.objects.all().order_by("-created_at")
        return Response(LoreTokenSignatureSerializer(sigs, many=True).data)

    serializer = LoreTokenSignatureSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sig = serializer.save()
    return Response(LoreTokenSignatureSerializer(sig).data, status=201)


@api_view(["POST"])
def myth_verification(request):
    token_id = request.data.get("token")
    token = get_object_or_404(LoreToken, id=token_id)
    result = verify_lore_token_signature(token)
    return Response({"verified": result})


@api_view(["POST"])
def chronomyth_sync(request):
    sync_chronomyth_state()
    return Response({"status": "ok"})

@api_view(["GET", "POST"])
def belief_forks(request):
    if request.method == "GET":
        forks = BeliefForkEvent.objects.all().order_by("-created_at")
        return Response(BeliefForkEventSerializer(forks, many=True).data)

    serializer = BeliefForkEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    fork = serializer.save()
    return Response(BeliefForkEventSerializer(fork).data, status=201)


@api_view(["GET", "POST"])
def myth_collapses(request):
    if request.method == "GET":
        logs = MythCollapseLog.objects.all().order_by("-created_at")
        return Response(MythCollapseLogSerializer(logs, many=True).data)

    serializer = MythCollapseLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log = serializer.save()
    return Response(MythCollapseLogSerializer(log).data, status=201)


@api_view(["GET", "POST"])
def memory_reformations(request):
    if request.method == "GET":
        rituals = MemoryReformationRitual.objects.all().order_by("-created_at")
        return Response(MemoryReformationRitualSerializer(rituals, many=True).data)

    serializer = MemoryReformationRitualSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ritual = serializer.save()
    return Response(MemoryReformationRitualSerializer(ritual).data, status=201)


@api_view(["GET", "POST"])
def epistemology(request):
    if request.method == "GET":
        nodes = EpistemologyNode.objects.all().order_by("-created_at")
        return Response(EpistemologyNodeSerializer(nodes, many=True).data)

    serializer = EpistemologyNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    node = serializer.save()
    return Response(EpistemologyNodeSerializer(node).data, status=201)


@api_view(["GET", "POST"])
def entanglements(request):
    if request.method == "GET":
        links = BeliefEntanglementLink.objects.all().order_by("-created_at")
        return Response(BeliefEntanglementLinkSerializer(links, many=True).data)

    serializer = BeliefEntanglementLinkSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    link = serializer.save()
    return Response(BeliefEntanglementLinkSerializer(link).data, status=201)


@api_view(["GET", "POST"])
def cognitive_constraints(request):
    if request.method == "GET":
        profiles = CognitiveConstraintProfile.objects.all().order_by("-created_at")
        return Response(CognitiveConstraintProfileSerializer(profiles, many=True).data)

    serializer = CognitiveConstraintProfileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    profile = serializer.save()
    return Response(CognitiveConstraintProfileSerializer(profile).data, status=201)
