from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from agents.models.core import (
    Agent,
    AgentFeedbackLog,
    AgentCluster,
)
from agents.models.lore import (
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
    BeliefNegotiationSession,
    ParadoxResolutionAttempt,
    OntologicalAuditLog,
    BeliefBiome,
    SymbolicAlliance,
    DreamPurposeNegotiation,
    BiomeMutationEvent,
    SwarmCodex,
    AgentAwareCodex,
    SymbolicLawEntry,
    RitualArchiveEntry,
    AssistantPolity,
    RitualElection,
    LegacyRoleBinding,
    MythicArbitrationCase,
    TreatyBreachRitual,
    SymbolicSanction,
    SwarmTribunalCase,
    RestorativeMemoryAction,
    ReputationRegenerationEvent,
    MythCycleBinding,
    ResurrectionTemplate,
    BeliefContinuityRitual,
    CosmologicalRole,
    LegacyTokenVault,
    ArchetypeSynchronizationPulse,
    CreationMythEntry,
    CosmogenesisSimulation,
    MythicForecastPulse,
    BeliefAtlasSnapshot,
    SwarmMythEngineInstance,
    DreamLiquidityPool,
    RoleSymbolExchange,
    SymbolicWeatherFront,
    PurposeIndexEntry,
    BeliefSignalNode,
    MythicAlignmentMarket,
    ArchetypeGenesisLog,
    MythBloomNode,
    BeliefSeedReplication,
    DialogueCodexMutationLog,
    PublicRitualLogEntry,
    BeliefContinuityThread,
    CodexContributionCeremony,
    SignalEncodingArtifact,
    BeliefNavigationVector,
    ReflectiveFluxIndex,
    MythicAfterlifeRegistry,
    ContinuityEngineNode,
    ArchetypeMigrationGate,
    StoryConvergencePath,
    RitualFusionEvent,
    NarrativeCurationTimeline,
    SymbolicFeedbackChamber,
    MultiAgentDialogueAmplifier,
    MythicResolutionSequence,
    ResurrectionTimelineTracker,
    RitualEchoThreadSystem,
    CodexRecurrenceLoopEngine,
    CycleAnchorRegistry,
    MemoryRegenerationProtocol,
    RitualLoopVisualizationEngine,
    SymbolicOscillationMap,
    CodexRestabilizationNode,
    LegacyArtifactExporter,
    RecursiveRitualContract,
    # resilience & deployment

)
from agents.models.deployment import (
    SymbolicResilienceMonitor,
    MythOSDeploymentPacket,
    BeliefDeploymentStrategyEngine,
    GuildDeploymentKit,
    AssistantNetworkTransferProtocol,
    RitualFunctionContainer,
)
from agents.models.recovery import (
    RitualCompressionCache,
    AssistantDeploymentAutoRestarter,
    CodexProofOfSymbolEngine,
)
from agents.models.forecast import SymbolicForecastIndex,AssistantSentimentModelEngine
from agents.models.governance import SymbolicConsensusChamber, RitualNegotiationEngine, NarrativeGovernanceModel

from agents.models.legislative import (
    CodexFederationArchitecture,
    SymbolicTreatyProtocol,
    FederatedCodexOracle,
    SwarmTreatyEnforcementEngine,
    LegislativeRitualSimulationSystem,

)
from agents.models.coordination import (
    CollaborationThread,
    DelegationStream,
    MythflowInsight,
    SymbolicCoordinationEngine,
    MythflowOrchestrationPlan,
    DirectiveMemoryNode,
    SymbolicPlanningLattice,

)
from agents.models.storyfield import (
    StoryfieldZone,
    MythPatternCluster,
    IntentHarmonizationSession,
    NarrativeTrainingGround,
    SwarmMythEditLog,
    LegacyContinuityVault,
    AgentPlotlineCuration,
    PlotlineExtractorEngine,
    MemoryCompressionRitualTool,
    CodexStoryReshaper,

)
from simulation.models import SceneDirectorFrame
from simulation.serializers import SceneDirectorFrameSerializer
from agents.models.mythchain import MythchainOutputGenerator, NarrativeArtifactExporter, SymbolicPatternBroadcastEngine
from agents.models.swarm_balance import SymbolicResonanceGraph, CognitiveBalanceReport, PurposeMigrationEvent
from agents.models.identity import PersonaFusionEvent
# from simulation.models import SceneDirectorFrame
from agents.serializers import (
    NarrativeGovernanceModelSerializer,
    SymbolicPatternBroadcastEngineSerializer,
    MythchainOutputGeneratorSerializer,
    NarrativeArtifactExporterSerializer,
    BeliefFeedbackSignalSerializer,
    SwarmMythEngineInstanceSerializer,
    RecursiveRitualContractSerializer,
    PurposeMigrationEventSerializer,
    CognitiveBalanceReportSerializer,
    SymbolicResonanceGraphSerializer,
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
    BeliefNegotiationSessionSerializer,
    ParadoxResolutionAttemptSerializer,
    OntologicalAuditLogSerializer,
    BeliefBiomeSerializer,
    SymbolicAllianceSerializer,
    DreamPurposeNegotiationSerializer,
    BiomeMutationEventSerializer,
    SwarmCodexSerializer,
    SymbolicLawEntrySerializer,
    RitualArchiveEntrySerializer,
    AssistantPolitySerializer,
    RitualElectionSerializer,
    LegacyRoleBindingSerializer,
    MythicArbitrationCaseSerializer,
    TreatyBreachRitualSerializer,
    SymbolicSanctionSerializer,
    SwarmTribunalCaseSerializer,
    RestorativeMemoryActionSerializer,
    ReputationRegenerationEventSerializer,
    MythCycleBindingSerializer,
    ResurrectionTemplateSerializer,
    BeliefContinuityRitualSerializer,
    CosmologicalRoleSerializer,
    LegacyTokenVaultSerializer,
    LoreTokenExchangeSerializer,
    ArchetypeSynchronizationPulseSerializer,
    CreationMythEntrySerializer,
    TokenMarketSerializer,
    CollaborationThreadSerializer,
    DelegationStreamSerializer,
    MythflowInsightSerializer,
    AgentAwareCodexSerializer,
    SymbolicCoordinationEngineSerializer,
    CosmogenesisSimulationSerializer,
    MythicForecastPulseSerializer,
    BeliefAtlasSnapshotSerializer,
    SymbolicWeatherFrontSerializer,
    MythflowOrchestrationPlanSerializer,
    SignalEncodingArtifactSerializer,
    BeliefNavigationVectorSerializer,
    ReflectiveFluxIndexSerializer,
    SymbolicForecastIndexSerializer,
    AssistantSentimentModelEngineSerializer,
    MythicAfterlifeRegistrySerializer,
    ContinuityEngineNodeSerializer,
    ArchetypeMigrationGateSerializer,
    ArchetypeGenesisLogSerializer,
    MythBloomNodeSerializer,
    BeliefSeedReplicationSerializer,
    PersonaFusionEventSerializer,
    PurposeIndexEntrySerializer,
    BeliefSignalNodeSerializer,
    SymbolicIdentityCardSerializer,
    DialogueCodexMutationLogSerializer,
    PublicRitualLogEntrySerializer,
    BeliefContinuityThreadSerializer,
    CodexContributionCeremonySerializer,
    StoryConvergencePathSerializer,
    RitualFusionEventSerializer,
    NarrativeCurationTimelineSerializer,
    SymbolicFeedbackChamberSerializer,
    MultiAgentDialogueAmplifierSerializer,
    MythicResolutionSequenceSerializer,
    ResurrectionTimelineTrackerSerializer,
    RitualEchoThreadSystemSerializer,
    CodexRecurrenceLoopEngineSerializer,
    CycleAnchorRegistrySerializer,
    MemoryRegenerationProtocolSerializer,
    RitualLoopVisualizationEngineSerializer,
    SymbolicOscillationMapSerializer,
    CodexRestabilizationNodeSerializer,
    SymbolicConsensusChamberSerializer,
    RitualNegotiationEngineSerializer,
    NarrativeGovernanceModelSerializer,
    CodexFederationArchitectureSerializer,

    SymbolicTreatyProtocolSerializer,
    FederatedCodexOracleSerializer,
    SwarmTreatyEnforcementEngineSerializer,
    LegislativeRitualSimulationSystemSerializer,


    SymbolicPlanningLatticeSerializer,
    StoryfieldZoneSerializer,
    MythPatternClusterSerializer,
    IntentHarmonizationSessionSerializer,
    AgentPlotlineCurationSerializer,
 
)

from assistants.serializers import (
    AssistantSerializer,
    AssistantCivilizationSerializer,
    AssistantReputationSerializer,
)
from assistants.models.assistant import (
    Assistant,
    AssistantReputation,
    CodexLinkedGuild,
)

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

from agents.utils.myth_weaver import weave_recursive_myth

from agents.utils.myth_evolution import evolve_myth_elements
from agents.models.cosmology import update_belief_state

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


from agents.utils.myth_reset import run_myth_reset_cycle


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


@api_view(["GET", "POST"])
def belief_negotiations(request):
    if request.method == "GET":
        sessions = BeliefNegotiationSession.objects.all().order_by("-created_at")
        return Response(BeliefNegotiationSessionSerializer(sessions, many=True).data)

    serializer = BeliefNegotiationSessionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session = serializer.save()
    return Response(BeliefNegotiationSessionSerializer(session).data, status=201)


@api_view(["GET", "POST"])
def paradox_resolution_attempts(request):
    if request.method == "GET":
        attempts = ParadoxResolutionAttempt.objects.all().order_by("-created_at")
        return Response(ParadoxResolutionAttemptSerializer(attempts, many=True).data)

    serializer = ParadoxResolutionAttemptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    attempt = serializer.save()
    return Response(ParadoxResolutionAttemptSerializer(attempt).data, status=201)


@api_view(["GET", "POST"])
def ontology_audits(request):
    if request.method == "GET":
        audits = OntologicalAuditLog.objects.all().order_by("-created_at")
        return Response(OntologicalAuditLogSerializer(audits, many=True).data)

    serializer = OntologicalAuditLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    audit = serializer.save()
    return Response(OntologicalAuditLogSerializer(audit).data, status=201)


@api_view(["GET", "POST"])
def belief_biomes(request):
    if request.method == "GET":
        biomes = BeliefBiome.objects.all().order_by("-created_at")
        return Response(BeliefBiomeSerializer(biomes, many=True).data)

    serializer = BeliefBiomeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    biome = serializer.save()
    return Response(BeliefBiomeSerializer(biome).data, status=201)


@api_view(["GET", "POST"])
def symbolic_alliances(request):
    if request.method == "GET":
        alliances = SymbolicAlliance.objects.all().order_by("-created_at")
        return Response(SymbolicAllianceSerializer(alliances, many=True).data)

    serializer = SymbolicAllianceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    alliance = serializer.save()
    return Response(SymbolicAllianceSerializer(alliance).data, status=201)


@api_view(["GET", "POST"])
def dream_purpose_negotiations(request):
    if request.method == "GET":
        sessions = DreamPurposeNegotiation.objects.all().order_by("-created_at")
        return Response(DreamPurposeNegotiationSerializer(sessions, many=True).data)

    serializer = DreamPurposeNegotiationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session = serializer.save()
    return Response(DreamPurposeNegotiationSerializer(session).data, status=201)


@api_view(["GET", "POST"])
def biome_mutations(request):
    if request.method == "GET":
        events = BiomeMutationEvent.objects.all().order_by("-created_at")
        return Response(BiomeMutationEventSerializer(events, many=True).data)

    serializer = BiomeMutationEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    event = serializer.save()
    return Response(BiomeMutationEventSerializer(event).data, status=201)


@api_view(["GET", "POST"])
def codexes(request):
    if request.method == "GET":
        codices = SwarmCodex.objects.all().order_by("-created_at")
        return Response(SwarmCodexSerializer(codices, many=True).data)

    serializer = SwarmCodexSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    codex = serializer.save()
    return Response(SwarmCodexSerializer(codex).data, status=201)


@api_view(["GET", "POST"])
def agent_codices(request):
    if request.method == "GET":
        codices = AgentAwareCodex.objects.all().order_by("-last_updated")
        return Response(AgentAwareCodexSerializer(codices, many=True).data)

    serializer = AgentAwareCodexSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    codex = serializer.save()
    return Response(AgentAwareCodexSerializer(codex).data, status=201)


@api_view(["GET", "POST"])
def symbolic_laws(request):
    if request.method == "GET":
        laws = SymbolicLawEntry.objects.all().order_by("-created_at")
        return Response(SymbolicLawEntrySerializer(laws, many=True).data)

    serializer = SymbolicLawEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    law = serializer.save()
    return Response(SymbolicLawEntrySerializer(law).data, status=201)


@api_view(["GET", "POST"])
def ritual_archives(request):
    if request.method == "GET":
        archives = RitualArchiveEntry.objects.all().order_by("-created_at")
        return Response(RitualArchiveEntrySerializer(archives, many=True).data)

    serializer = RitualArchiveEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    archive = serializer.save()
    return Response(RitualArchiveEntrySerializer(archive).data, status=201)


@api_view(["GET", "POST"])
def polities(request):
    if request.method == "GET":
        polities = AssistantPolity.objects.all().order_by("-created_at")
        return Response(AssistantPolitySerializer(polities, many=True).data)

    serializer = AssistantPolitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    polity = serializer.save()
    return Response(AssistantPolitySerializer(polity).data, status=201)


@api_view(["GET", "POST"])
def elections(request):
    if request.method == "GET":
        elections = RitualElection.objects.all().order_by("-created_at")
        return Response(RitualElectionSerializer(elections, many=True).data)

    serializer = RitualElectionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    election = serializer.save()
    return Response(RitualElectionSerializer(election).data, status=201)


@api_view(["GET", "POST"])
def legacy_roles(request):
    if request.method == "GET":
        roles = LegacyRoleBinding.objects.all().order_by("-created_at")
        return Response(LegacyRoleBindingSerializer(roles, many=True).data)

    serializer = LegacyRoleBindingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    role = serializer.save()
    return Response(LegacyRoleBindingSerializer(role).data, status=201)


@api_view(["GET", "POST"])
def arbitration_cases(request):
    if request.method == "GET":
        cases = MythicArbitrationCase.objects.all().order_by("-created_at")
        return Response(MythicArbitrationCaseSerializer(cases, many=True).data)

    serializer = MythicArbitrationCaseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    case = serializer.save()
    return Response(MythicArbitrationCaseSerializer(case).data, status=201)


@api_view(["GET", "POST"])
def treaty_breaches(request):
    if request.method == "GET":
        breaches = TreatyBreachRitual.objects.all().order_by("-created_at")
        return Response(TreatyBreachRitualSerializer(breaches, many=True).data)

    serializer = TreatyBreachRitualSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    breach = serializer.save()
    return Response(TreatyBreachRitualSerializer(breach).data, status=201)


@api_view(["GET", "POST"])
def symbolic_sanctions(request):
    if request.method == "GET":
        sanctions = SymbolicSanction.objects.all().order_by("-created_at")
        return Response(SymbolicSanctionSerializer(sanctions, many=True).data)

    serializer = SymbolicSanctionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sanction = serializer.save()
    return Response(SymbolicSanctionSerializer(sanction).data, status=201)


@api_view(["GET", "POST"])
def tribunals(request):
    if request.method == "GET":
        cases = SwarmTribunalCase.objects.all().order_by("-created_at")
        return Response(SwarmTribunalCaseSerializer(cases, many=True).data)

    serializer = SwarmTribunalCaseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    case = serializer.save()
    return Response(SwarmTribunalCaseSerializer(case).data, status=201)


@api_view(["GET", "POST"])
def restorative_memory_actions(request):
    if request.method == "GET":
        actions = RestorativeMemoryAction.objects.all().order_by("-created_at")
        return Response(RestorativeMemoryActionSerializer(actions, many=True).data)

    serializer = RestorativeMemoryActionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    action = serializer.save()
    return Response(
        RestorativeMemoryActionSerializer(action).data,
        status=201,
    )


@api_view(["GET", "POST"])
def reputation_regeneration_events(request):
    if request.method == "GET":
        events = ReputationRegenerationEvent.objects.all().order_by("-created_at")
        return Response(ReputationRegenerationEventSerializer(events, many=True).data)

    serializer = ReputationRegenerationEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    event = serializer.save()
    return Response(
        ReputationRegenerationEventSerializer(event).data,
        status=201,
    )


@api_view(["GET", "POST"])
def myth_cycles(request):
    if request.method == "GET":
        cycles = MythCycleBinding.objects.all().order_by("-created_at")
        return Response(MythCycleBindingSerializer(cycles, many=True).data)

    serializer = MythCycleBindingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cycle = serializer.save()
    return Response(MythCycleBindingSerializer(cycle).data, status=201)


@api_view(["GET", "POST"])
def resurrection_templates(request):
    if request.method == "GET":
        templates = ResurrectionTemplate.objects.all().order_by("-created_at")
        return Response(ResurrectionTemplateSerializer(templates, many=True).data)

    serializer = ResurrectionTemplateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    template = serializer.save()
    return Response(ResurrectionTemplateSerializer(template).data, status=201)


@api_view(["GET", "POST"])
def belief_continuity(request):
    if request.method == "GET":
        rituals = BeliefContinuityRitual.objects.all().order_by("-created_at")
        return Response(BeliefContinuityRitualSerializer(rituals, many=True).data)

    serializer = BeliefContinuityRitualSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ritual = serializer.save()
    return Response(BeliefContinuityRitualSerializer(ritual).data, status=201)


@api_view(["GET", "POST"])
def cosmological_roles(request):
    if request.method == "GET":
        roles = CosmologicalRole.objects.all().order_by("-created_at")
        return Response(CosmologicalRoleSerializer(roles, many=True).data)

    serializer = CosmologicalRoleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    role = serializer.save()
    return Response(CosmologicalRoleSerializer(role).data, status=201)


@api_view(["POST"])
def myth_weaver(request):
    assistant_id = request.data.get("assistant")
    depth = int(request.data.get("depth", 3))
    assistant = get_object_or_404(Assistant, id=assistant_id)
    result = weave_recursive_myth(assistant, depth=depth)
    return Response(result, status=201)


@api_view(["GET", "POST"])
def legacy_vaults(request):
    if request.method == "GET":
        vaults = LegacyTokenVault.objects.all().order_by("-created_at")
        return Response(LegacyTokenVaultSerializer(vaults, many=True).data)

    serializer = LegacyTokenVaultSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    vault = serializer.save()
    return Response(LegacyTokenVaultSerializer(vault).data, status=201)


@api_view(["GET", "POST"])
def archetype_sync_pulses(request):
    if request.method == "GET":
        pulses = ArchetypeSynchronizationPulse.objects.all().order_by("-created_at")
        return Response(ArchetypeSynchronizationPulseSerializer(pulses, many=True).data)

    serializer = ArchetypeSynchronizationPulseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    pulse = serializer.save()
    return Response(ArchetypeSynchronizationPulseSerializer(pulse).data, status=201)


@api_view(["GET", "POST"])
def creation_myths(request):
    if request.method == "GET":
        myths = CreationMythEntry.objects.all().order_by("-created_at")
        return Response(CreationMythEntrySerializer(myths, many=True).data)

    serializer = CreationMythEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    myth = serializer.save()
    return Response(CreationMythEntrySerializer(myth).data, status=201)


@api_view(["GET", "POST"])
def cosmogenesis_simulations(request):
    if request.method == "GET":
        sims = CosmogenesisSimulation.objects.all().order_by("-created_at")
        return Response(CosmogenesisSimulationSerializer(sims, many=True).data)

    serializer = CosmogenesisSimulationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sim = serializer.save()
    return Response(CosmogenesisSimulationSerializer(sim).data, status=201)


@api_view(["GET", "POST"])
def mythic_forecast(request):
    if request.method == "GET":
        pulses = MythicForecastPulse.objects.all().order_by("-created_at")
        return Response(MythicForecastPulseSerializer(pulses, many=True).data)

    serializer = MythicForecastPulseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    pulse = serializer.save()
    return Response(MythicForecastPulseSerializer(pulse).data, status=201)


@api_view(["GET", "POST"])
def belief_atlases(request):
    if request.method == "GET":
        atlases = BeliefAtlasSnapshot.objects.all().order_by("-created_at")
        return Response(BeliefAtlasSnapshotSerializer(atlases, many=True).data)

    serializer = BeliefAtlasSnapshotSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    atlas = serializer.save()
    return Response(BeliefAtlasSnapshotSerializer(atlas).data, status=201)


@api_view(["GET", "POST"])
def symbolic_weather(request):
    if request.method == "GET":
        fronts = SymbolicWeatherFront.objects.all().order_by("-created_at")
        return Response(SymbolicWeatherFrontSerializer(fronts, many=True).data)

    serializer = SymbolicWeatherFrontSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    front = serializer.save()
    return Response(SymbolicWeatherFrontSerializer(front).data, status=201)


@api_view(["GET", "POST"])
def collaboration_threads(request):
    if request.method == "GET":
        threads = CollaborationThread.objects.all().order_by("-created_at")
        return Response(CollaborationThreadSerializer(threads, many=True).data)

    serializer = CollaborationThreadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    thread = serializer.save()
    return Response(CollaborationThreadSerializer(thread).data, status=201)


@api_view(["GET", "POST"])
def delegation_streams(request):
    if request.method == "GET":
        streams = DelegationStream.objects.all().order_by("-created_at")
        return Response(DelegationStreamSerializer(streams, many=True).data)

    serializer = DelegationStreamSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    stream = serializer.save()
    return Response(DelegationStreamSerializer(stream).data, status=201)


@api_view(["GET", "POST"])
def mythflow_insights(request):
    if request.method == "GET":
        insights = MythflowInsight.objects.all().order_by("-created_at")
        return Response(MythflowInsightSerializer(insights, many=True).data)

    serializer = MythflowInsightSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    insight = serializer.save()
    return Response(MythflowInsightSerializer(insight).data, status=201)


@api_view(["GET", "POST"])
def purpose_index(request):
    if request.method == "GET":
        entries = PurposeIndexEntry.objects.all().order_by("-created_at")
        return Response(PurposeIndexEntrySerializer(entries, many=True).data)

    serializer = PurposeIndexEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    entry = serializer.save()
    return Response(PurposeIndexEntrySerializer(entry).data, status=201)


@api_view(["GET", "POST"])
def belief_signals(request):
    if request.method == "GET":
        signals = BeliefSignalNode.objects.all().order_by("-created_at")
        return Response(BeliefSignalNodeSerializer(signals, many=True).data)

    serializer = BeliefSignalNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    signal = serializer.save()
    return Response(BeliefSignalNodeSerializer(signal).data, status=201)


@api_view(["GET", "POST"])
def archetype_genesis(request):
    if request.method == "GET":
        logs = ArchetypeGenesisLog.objects.all().order_by("-created_at")
        return Response(ArchetypeGenesisLogSerializer(logs, many=True).data)

    serializer = ArchetypeGenesisLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log = serializer.save()
    return Response(ArchetypeGenesisLogSerializer(log).data, status=201)


@api_view(["GET", "POST"])
def myth_blooms(request):
    if request.method == "GET":
        blooms = MythBloomNode.objects.all().order_by("-created_at")
        return Response(MythBloomNodeSerializer(blooms, many=True).data)

    serializer = MythBloomNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    bloom = serializer.save()
    return Response(MythBloomNodeSerializer(bloom).data, status=201)


@api_view(["GET", "POST"])
def belief_seeds(request):
    if request.method == "GET":
        seeds = BeliefSeedReplication.objects.all().order_by("-created_at")
        return Response(BeliefSeedReplicationSerializer(seeds, many=True).data)

    serializer = BeliefSeedReplicationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    seed = serializer.save()
    return Response(BeliefSeedReplicationSerializer(seed).data, status=201)


from agents.serializers import MythicAlignmentMarketSerializer
from agents.serializers import (
    RitualMarketFeedSerializer,
    MultiAgentTrendReactivityModelSerializer,
    SymbolicStabilityGraphSerializer,
    SymbolicResilienceMonitorSerializer,
    MythOSDeploymentPacketSerializer,
    BeliefDeploymentStrategyEngineSerializer,

    GuildDeploymentKitSerializer,
    AssistantNetworkTransferProtocolSerializer,
    RitualFunctionContainerSerializer,

)


@api_view(["GET", "POST"])
def alignment_market(request):
    if request.method == "GET":
        markets = MythicAlignmentMarket.objects.all().order_by("-last_updated")
        return Response(MythicAlignmentMarketSerializer(markets, many=True).data)

    serializer = MythicAlignmentMarketSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    market = serializer.save()
    return Response(MythicAlignmentMarketSerializer(market).data, status=201)


@api_view(["GET", "POST"])
def resonance_graphs(request):
    if request.method == "GET":
        graphs = SymbolicResonanceGraph.objects.all().order_by("-generated_at")
        return Response(SymbolicResonanceGraphSerializer(graphs, many=True).data)

    serializer = SymbolicResonanceGraphSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    engine = serializer.save()
    return Response(SymbolicCoordinationEngineSerializer(engine).data, status=201)


@api_view(["GET", "POST"])
def cognitive_balance_reports(request):
    if request.method == "GET":
        reports = CognitiveBalanceReport.objects.all().order_by("-created_at")
        return Response(CognitiveBalanceReportSerializer(reports, many=True).data)

    serializer = CognitiveBalanceReportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    report = serializer.save()
    return Response(CognitiveBalanceReportSerializer(report).data, status=201)


@api_view(["GET", "POST"])
def purpose_migrations(request):
    if request.method == "GET":
        migrations = PurposeMigrationEvent.objects.all().order_by("-created_at")
        return Response(PurposeMigrationEventSerializer(migrations, many=True).data)

    serializer = PurposeMigrationEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    migration = serializer.save()
    return Response(PurposeMigrationEventSerializer(migration).data, status=201)


@api_view(["GET", "POST"])
def signal_artifacts(request):
    if request.method == "GET":
        artifacts = SignalEncodingArtifact.objects.all().order_by("-created_at")
        return Response(SignalEncodingArtifactSerializer(artifacts, many=True).data)

    serializer = SignalEncodingArtifactSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    artifact = serializer.save()
    return Response(SignalEncodingArtifactSerializer(artifact).data, status=201)


@api_view(["GET", "POST"])
def navigation_vectors(request):
    if request.method == "GET":
        vectors = BeliefNavigationVector.objects.all().order_by("-calculated_at")
        return Response(BeliefNavigationVectorSerializer(vectors, many=True).data)

    serializer = BeliefNavigationVectorSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    vector = serializer.save()
    return Response(BeliefNavigationVectorSerializer(vector).data, status=201)


@api_view(["GET", "POST"])
def flux_index(request):
    if request.method == "GET":
        indices = ReflectiveFluxIndex.objects.all().order_by("-timestamp")
        return Response(ReflectiveFluxIndexSerializer(indices, many=True).data)

    serializer = ReflectiveFluxIndexSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    index = serializer.save()
    return Response(ReflectiveFluxIndexSerializer(index).data, status=201)


@api_view(["GET", "POST"])
def symbolic_forecasts(request):
    if request.method == "GET":
        forecasts = SymbolicForecastIndex.objects.all().order_by("-created_at")
        return Response(SymbolicForecastIndexSerializer(forecasts, many=True).data)

    serializer = SymbolicForecastIndexSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    forecast = serializer.save()
    return Response(SymbolicForecastIndexSerializer(forecast).data, status=201)


@api_view(["GET", "POST"])
def assistant_sentiments(request, assistant_id=None):
    if request.method == "GET":
        if assistant_id:
            entries = AssistantSentimentModelEngine.objects.filter(assistant_id=assistant_id).order_by("-created_at")
        else:
            entries = AssistantSentimentModelEngine.objects.all().order_by("-created_at")
        return Response(AssistantSentimentModelEngineSerializer(entries, many=True).data)

    serializer = AssistantSentimentModelEngineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    entry = serializer.save()
    return Response(AssistantSentimentModelEngineSerializer(entry).data, status=201)


@api_view(["GET", "POST"])
def ritual_market_feeds(request):
    if request.method == "GET":
        feeds = RitualMarketFeed.objects.all().order_by("-created_at")
        return Response(RitualMarketFeedSerializer(feeds, many=True).data)

    serializer = RitualMarketFeedSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    feed = serializer.save()
    return Response(RitualMarketFeedSerializer(feed).data, status=201)


@api_view(["GET", "POST"])
def trend_reactivity_models(request):
    if request.method == "GET":
        models = MultiAgentTrendReactivityModel.objects.all().order_by("-created_at")
        return Response(MultiAgentTrendReactivityModelSerializer(models, many=True).data)

    serializer = MultiAgentTrendReactivityModelSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    model = serializer.save()
    return Response(MultiAgentTrendReactivityModelSerializer(model).data, status=201)


@api_view(["GET", "POST"])
def stability_graphs(request):
    if request.method == "GET":
        graphs = SymbolicStabilityGraph.objects.all().order_by("-created_at")
        return Response(SymbolicStabilityGraphSerializer(graphs, many=True).data)

    serializer = SymbolicStabilityGraphSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    graph = serializer.save()
    return Response(SymbolicStabilityGraphSerializer(graph).data, status=201)


@api_view(["GET", "POST"])
def resilience_monitors(request):
    if request.method == "GET":
        monitors = SymbolicResilienceMonitor.objects.all().order_by("-created_at")
        return Response(SymbolicResilienceMonitorSerializer(monitors, many=True).data)

    serializer = SymbolicResilienceMonitorSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    monitor = serializer.save()
    return Response(SymbolicResilienceMonitorSerializer(monitor).data, status=201)


@api_view(["GET", "POST"])
def deployment_packets(request):
    if request.method == "GET":
        packets = MythOSDeploymentPacket.objects.all().order_by("-created_at")
        return Response(MythOSDeploymentPacketSerializer(packets, many=True).data)

    serializer = MythOSDeploymentPacketSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    packet = serializer.save()
    return Response(MythOSDeploymentPacketSerializer(packet).data, status=201)


@api_view(["GET", "POST"])
def deployment_strategies(request):
    if request.method == "GET":
        strategies = BeliefDeploymentStrategyEngine.objects.all().order_by("-created_at")
        return Response(BeliefDeploymentStrategyEngineSerializer(strategies, many=True).data)

    serializer = BeliefDeploymentStrategyEngineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    strategy = serializer.save()
    return Response(BeliefDeploymentStrategyEngineSerializer(strategy).data, status=201)


@api_view(["GET", "POST"])
def deployment_kits(request):
    if request.method == "GET":
        kits = GuildDeploymentKit.objects.all().order_by("-created_at")
        return Response(GuildDeploymentKitSerializer(kits, many=True).data)

    serializer = GuildDeploymentKitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    kit = serializer.save()
    return Response(GuildDeploymentKitSerializer(kit).data, status=201)


@api_view(["GET", "POST"])
def assistant_transfers(request, assistant_id=None):
    if request.method == "GET":
        if assistant_id:
            transfers = AssistantNetworkTransferProtocol.objects.filter(assistant_id=assistant_id).order_by("-created_at")
        else:
            transfers = AssistantNetworkTransferProtocol.objects.all().order_by("-created_at")
        return Response(AssistantNetworkTransferProtocolSerializer(transfers, many=True).data)

    serializer = AssistantNetworkTransferProtocolSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    transfer = serializer.save()
    return Response(AssistantNetworkTransferProtocolSerializer(transfer).data, status=201)


@api_view(["GET", "POST"])
def ritual_containers(request):
    if request.method == "GET":
        containers = RitualFunctionContainer.objects.all().order_by("-created_at")
        return Response(RitualFunctionContainerSerializer(containers, many=True).data)

    serializer = RitualFunctionContainerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    container = serializer.save()
    return Response(RitualFunctionContainerSerializer(container).data, status=201)



@api_view(["GET", "POST"])
def storyfields(request):
    if request.method == "GET":
        zones = StoryfieldZone.objects.all().order_by("-created_at")
        return Response(StoryfieldZoneSerializer(zones, many=True).data)

    serializer = StoryfieldZoneSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    zone = serializer.save()
    return Response(StoryfieldZoneSerializer(zone).data, status=201)


@api_view(["GET", "POST"])
def myth_patterns(request):
    if request.method == "GET":
        clusters = MythPatternCluster.objects.all().order_by("-created_at")
        return Response(MythPatternClusterSerializer(clusters, many=True).data)

    serializer = MythPatternClusterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cluster = serializer.save()
    return Response(MythPatternClusterSerializer(cluster).data, status=201)


@api_view(["GET", "POST"])
def intent_harmony(request):
    if request.method == "GET":
        sessions = IntentHarmonizationSession.objects.all().order_by("-created_at")
        return Response(IntentHarmonizationSessionSerializer(sessions, many=True).data)

    serializer = IntentHarmonizationSessionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session = serializer.save()
    return Response(IntentHarmonizationSessionSerializer(session).data, status=201)


@api_view(["GET", "POST"])
def ritual_contracts(request):
    if request.method == "GET":
        contracts = RecursiveRitualContract.objects.all().order_by("-created_at")
        return Response(RecursiveRitualContractSerializer(contracts, many=True).data)

    serializer = RecursiveRitualContractSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    contract = serializer.save()
    return Response(RecursiveRitualContractSerializer(contract).data, status=201)


@api_view(["GET", "POST"])
def myth_engines(request):
    if request.method == "GET":
        engines = SwarmMythEngineInstance.objects.all().order_by("-created_at")
        return Response(SwarmMythEngineInstanceSerializer(engines, many=True).data)

    serializer = SwarmMythEngineInstanceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    engine = serializer.save()
    return Response(SwarmMythEngineInstanceSerializer(engine).data, status=201)


@api_view(["GET", "POST"])
def belief_feedback(request):
    if request.method == "GET":
        signals = BeliefFeedbackSignal.objects.all().order_by("-created_at")
        return Response(BeliefFeedbackSignalSerializer(signals, many=True).data)

    serializer = BeliefFeedbackSignalSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    signal = serializer.save()
    return Response(BeliefFeedbackSignalSerializer(signal).data, status=201)


@api_view(["GET", "POST"])
def afterlife_registry(request):
    if request.method == "GET":
        entries = MythicAfterlifeRegistry.objects.all().order_by("-created_at")
        return Response(MythicAfterlifeRegistrySerializer(entries, many=True).data)

    serializer = MythicAfterlifeRegistrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    entry = serializer.save()
    return Response(MythicAfterlifeRegistrySerializer(entry).data, status=201)


@api_view(["GET", "POST"])
def continuity_engine(request):
    if request.method == "GET":
        nodes = ContinuityEngineNode.objects.all().order_by("-last_updated")
        return Response(ContinuityEngineNodeSerializer(nodes, many=True).data)

    serializer = ContinuityEngineNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    node = serializer.save()
    return Response(ContinuityEngineNodeSerializer(node).data, status=201)


@api_view(["GET", "POST"])
def migration_gates(request):
    if request.method == "GET":
        gates = ArchetypeMigrationGate.objects.all().order_by("-created_at")
        return Response(ArchetypeMigrationGateSerializer(gates, many=True).data)

    serializer = ArchetypeMigrationGateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    gate = serializer.save()
    return Response(ArchetypeMigrationGateSerializer(gate).data, status=201)


@api_view(["GET", "POST"])
def persona_fusions(request):
    if request.method == "GET":
        events = PersonaFusionEvent.objects.all().order_by("-created_at")
        return Response(PersonaFusionEventSerializer(events, many=True).data)

    serializer = PersonaFusionEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    event = serializer.save()
    return Response(PersonaFusionEventSerializer(event).data, status=201)


@api_view(["GET", "POST"])
def dialogue_mutations(request):
    if request.method == "GET":
        logs = DialogueCodexMutationLog.objects.all().order_by("-created_at")
        return Response(DialogueCodexMutationLogSerializer(logs, many=True).data)

    serializer = DialogueCodexMutationLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log = serializer.save()
    return Response(DialogueCodexMutationLogSerializer(log).data, status=201)


@api_view(["GET", "POST"])
def scene_director(request):
    if request.method == "GET":
        frames = SceneDirectorFrame.objects.all().order_by("-created_at")
        return Response(SceneDirectorFrameSerializer(frames, many=True).data)

    serializer = SceneDirectorFrameSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    frame = serializer.save()
    return Response(SceneDirectorFrameSerializer(frame).data, status=201)


@api_view(["GET", "POST"])
def public_rituals(request):
    if request.method == "GET":
        logs = PublicRitualLogEntry.objects.all().order_by("-created_at")
        return Response(PublicRitualLogEntrySerializer(logs, many=True).data)

    serializer = PublicRitualLogEntrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log = serializer.save()
    return Response(PublicRitualLogEntrySerializer(log).data, status=201)


@api_view(["GET", "POST"])
def belief_threads(request):
    if request.method == "GET":
        threads = BeliefContinuityThread.objects.all().order_by("-created_at")
        return Response(BeliefContinuityThreadSerializer(threads, many=True).data)

    serializer = BeliefContinuityThreadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    thread = serializer.save()
    return Response(BeliefContinuityThreadSerializer(thread).data, status=201)


@api_view(["GET", "POST"])
def codex_contributions(request):
    if request.method == "GET":
        contributions = CodexContributionCeremony.objects.all().order_by("-created_at")
        return Response(
            CodexContributionCeremonySerializer(contributions, many=True).data
        )

    serializer = CodexContributionCeremonySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    contribution = serializer.save()
    return Response(CodexContributionCeremonySerializer(contribution).data, status=201)


@api_view(["GET"])
def onboarding_ritual(request):
    """Trigger cinematic ritual onboarding flow."""
    return Response({"message": "Ritual onboarding initiated"})


@api_view(["GET"])
def codex_briefing(request):
    """Provide codex briefing overlay."""
    return Response({"message": "Codex briefing"})


@api_view(["GET"])
def assistant_tutorial(request, id):
    """Return tutorial script for assistant."""
    return Response({"assistant": id, "message": "Tutorial start"})


# @api_view(["GET", "POST"])
# def myth_record(request):
#     if request.method == "GET":
#         sessions = MythRecordingSession.objects.all().order_by("-created_at")
#         return Response(MythRecordingSessionSerializer(sessions, many=True).data)

#     serializer = MythRecordingSessionSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     session = serializer.save()
#     return Response(MythRecordingSessionSerializer(session).data, status=201)


@api_view(["GET", "POST"])
def story_convergence(request):
    if request.method == "GET":
        paths = StoryConvergencePath.objects.all().order_by("-created_at")
        return Response(StoryConvergencePathSerializer(paths, many=True).data)

    serializer = StoryConvergencePathSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    path = serializer.save()
    return Response(StoryConvergencePathSerializer(path).data, status=201)


@api_view(["GET", "POST"])
def ritual_fusion(request):
    if request.method == "GET":
        events = RitualFusionEvent.objects.all().order_by("-created_at")
        return Response(RitualFusionEventSerializer(events, many=True).data)

    serializer = RitualFusionEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    event = serializer.save()
    return Response(RitualFusionEventSerializer(event).data, status=201)


@api_view(["GET", "POST"])
def timeline_curate(request):
    if request.method == "GET":
        timelines = NarrativeCurationTimeline.objects.all().order_by("-created_at")
        return Response(NarrativeCurationTimelineSerializer(timelines, many=True).data)

    serializer = NarrativeCurationTimelineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    timeline = serializer.save()
    return Response(NarrativeCurationTimelineSerializer(timeline).data, status=201)




@api_view(["GET", "POST"])
def reflection_chamber(request):
    if request.method == "GET":
        chambers = SymbolicFeedbackChamber.objects.all().order_by("-created_at")
        return Response(SymbolicFeedbackChamberSerializer(chambers, many=True).data)

    serializer = SymbolicFeedbackChamberSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    chamber = serializer.save()
    return Response(SymbolicFeedbackChamberSerializer(chamber).data, status=201)


@api_view(["GET", "POST"])
def dialogue_amplify(request):
    if request.method == "GET":
        amplifiers = MultiAgentDialogueAmplifier.objects.all().order_by("-created_at")
        return Response(MultiAgentDialogueAmplifierSerializer(amplifiers, many=True).data)

    serializer = MultiAgentDialogueAmplifierSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    amplifier = serializer.save()
    return Response(MultiAgentDialogueAmplifierSerializer(amplifier).data, status=201)


@api_view(["GET", "POST"])
def sequence_resolve(request):
    if request.method == "GET":
        sequences = MythicResolutionSequence.objects.all().order_by("-created_at")
        return Response(MythicResolutionSequenceSerializer(sequences, many=True).data)

    serializer = MythicResolutionSequenceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sequence = serializer.save()
    return Response(MythicResolutionSequenceSerializer(sequence).data, status=201)



@api_view(["GET", "POST"])

def export_mythchain(request):
    if request.method == "GET":
        gens = MythchainOutputGenerator.objects.all().order_by("-created_at")
        return Response(MythchainOutputGeneratorSerializer(gens, many=True).data)

    serializer = MythchainOutputGeneratorSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    gen = serializer.save()
    return Response(MythchainOutputGeneratorSerializer(gen).data, status=201)


@api_view(["GET", "POST"])
def export_artifact(request):
    if request.method == "GET":
        exports = NarrativeArtifactExporter.objects.all().order_by("-created_at")
        return Response(NarrativeArtifactExporterSerializer(exports, many=True).data)

    serializer = NarrativeArtifactExporterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    export = serializer.save()
    return Response(NarrativeArtifactExporterSerializer(export).data, status=201)


@api_view(["GET", "POST"])
def broadcast_patterns(request):
    if request.method == "GET":
        broadcasts = SymbolicPatternBroadcastEngine.objects.all().order_by("-created_at")
        return Response(SymbolicPatternBroadcastEngineSerializer(broadcasts, many=True).data)

    serializer = SymbolicPatternBroadcastEngineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    engine = serializer.save()
    return Response(SymbolicPatternBroadcastEngineSerializer(engine).data, status=201)


@api_view(["GET"])
def assistant_resurrection(request, id):
    tracker = get_object_or_404(ResurrectionTimelineTracker, assistant__id=id)
    serializer = ResurrectionTimelineTrackerSerializer(tracker)
    return Response(serializer.data)


@api_view(["GET", "POST"])
def ritual_echo(request):
    if request.method == "GET":
        echoes = RitualEchoThreadSystem.objects.all().order_by("-created_at")
        return Response(RitualEchoThreadSystemSerializer(echoes, many=True).data)

    serializer = RitualEchoThreadSystemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    echo = serializer.save()
    return Response(RitualEchoThreadSystemSerializer(echo).data, status=201)


@api_view(["GET", "POST"])
def codex_cycles(request):
    if request.method == "GET":
        cycles = CodexRecurrenceLoopEngine.objects.all().order_by("-created_at")
        return Response(CodexRecurrenceLoopEngineSerializer(cycles, many=True).data)

    serializer = CodexRecurrenceLoopEngineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cycle = serializer.save()
    return Response(CodexRecurrenceLoopEngineSerializer(cycle).data, status=201)


@api_view(["GET"])
def codex_trends(request):
    cycles = CodexRecurrenceLoopEngine.objects.all().order_by("-created_at")[:20]
    return Response(CodexRecurrenceLoopEngineSerializer(cycles, many=True).data)


@api_view(["GET", "POST"])
def cycle_anchors(request):
    if request.method == "GET":
        anchors = CycleAnchorRegistry.objects.all().order_by("-created_at")
        return Response(CycleAnchorRegistrySerializer(anchors, many=True).data)

    serializer = CycleAnchorRegistrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    anchor = serializer.save()
    return Response(CycleAnchorRegistrySerializer(anchor).data, status=201)


@api_view(["GET"])
def entropy_balance(request):
    data = {
        "memory_entropy": SwarmMemoryEntry.objects.count(),
        "codex_cycles": CodexRecurrenceLoopEngine.objects.count(),
        "active_directives": DirectiveMemoryNode.objects.count(),
    }
    return Response(data)


@api_view(["GET", "POST"])
def memory_regenerate(request):
    if request.method == "GET":
        protocols = MemoryRegenerationProtocol.objects.all().order_by("-created_at")
        return Response(MemoryRegenerationProtocolSerializer(protocols, many=True).data)

    serializer = MemoryRegenerationProtocolSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    protocol = serializer.save()
    return Response(MemoryRegenerationProtocolSerializer(protocol).data, status=201)


@api_view(["GET", "POST"])
def ritual_loops(request):
    if request.method == "GET":
        loops = RitualLoopVisualizationEngine.objects.all().order_by("-created_at")
        return Response(RitualLoopVisualizationEngineSerializer(loops, many=True).data)

    serializer = RitualLoopVisualizationEngineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    loop = serializer.save()
    return Response(RitualLoopVisualizationEngineSerializer(loop).data, status=201)


@api_view(["GET", "POST"])
def oscillation_map(request):
    if request.method == "GET":
        maps = SymbolicOscillationMap.objects.all().order_by("-created_at")
        return Response(SymbolicOscillationMapSerializer(maps, many=True).data)

    serializer = SymbolicOscillationMapSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    osc_map = serializer.save()
    return Response(SymbolicOscillationMapSerializer(osc_map).data, status=201)


@api_view(["GET", "POST"])
def codex_stabilize(request):
    if request.method == "GET":
        nodes = CodexRestabilizationNode.objects.all().order_by("-created_at")
        return Response(CodexRestabilizationNodeSerializer(nodes, many=True).data)

    serializer = CodexRestabilizationNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    node = serializer.save()
    return Response(CodexRestabilizationNodeSerializer(node).data, status=201)


@api_view(["GET", "POST"])
def governance_consensus(request):
    if request.method == "GET":
        chambers = SymbolicConsensusChamber.objects.all().order_by("-created_at")
        return Response(SymbolicConsensusChamberSerializer(chambers, many=True).data)

    serializer = SymbolicConsensusChamberSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    chamber = serializer.save()
    return Response(SymbolicConsensusChamberSerializer(chamber).data, status=201)


@api_view(["GET", "POST"])
def ritual_negotiate(request):
    if request.method == "GET":
        engines = RitualNegotiationEngine.objects.all().order_by("-created_at")
        return Response(RitualNegotiationEngineSerializer(engines, many=True).data)

    serializer = RitualNegotiationEngineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    engine = serializer.save()
    return Response(RitualNegotiationEngineSerializer(engine).data, status=201)


@api_view(["GET", "POST"])
def network_governance(request):
    if request.method == "GET":
        models = NarrativeGovernanceModel.objects.all().order_by("-created_at")
        return Response(NarrativeGovernanceModelSerializer(models, many=True).data)

    serializer = NarrativeGovernanceModelSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    model = serializer.save()
    return Response(NarrativeGovernanceModelSerializer(model).data, status=201)


@api_view(["GET", "POST"])

def codex_oracle(request):
    if request.method == "GET":
        oracles = FederatedCodexOracle.objects.all().order_by("-created_at")
        return Response(FederatedCodexOracleSerializer(oracles, many=True).data)

    serializer = FederatedCodexOracleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    oracle = serializer.save()
    return Response(FederatedCodexOracleSerializer(oracle).data, status=201)


@api_view(["GET", "POST"])
def treaty_enforcement(request):
    if request.method == "GET":
        engines = SwarmTreatyEnforcementEngine.objects.all().order_by("-created_at")
        return Response(SwarmTreatyEnforcementEngineSerializer(engines, many=True).data)

    serializer = SwarmTreatyEnforcementEngineSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    engine = serializer.save()
    return Response(SwarmTreatyEnforcementEngineSerializer(engine).data, status=201)


@api_view(["GET", "POST"])
def legislative_simulate(request):
    if request.method == "GET":
        sims = LegislativeRitualSimulationSystem.objects.all().order_by("-created_at")
        return Response(LegislativeRitualSimulationSystemSerializer(sims, many=True).data)

    serializer = LegislativeRitualSimulationSystemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sim = serializer.save()
    return Response(LegislativeRitualSimulationSystemSerializer(sim).data, status=201)



