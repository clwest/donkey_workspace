from rest_framework import serializers
from agents.models.core import (
    Agent,
    AgentFeedbackLog,
    AgentCluster,
)
from agents.models.lore import (
    SwarmMemoryEntry,
    SwarmJournalEntry,
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
    LoreTokenExchange,
    TokenMarket,
    LoreTokenCraftingRitual,
    LoreTokenSignature,
    TokenGuildVote,
    MythRegistryEntry,
    TemporalLoreAnchor,
    RitualComplianceRecord,
    BeliefForkEvent,
    MythCollapseLog,
    MemoryReformationRitual,
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
    SymbolicWeatherFront,
    KnowledgeReplicationEvent,
    MemoryBroadcastPacket,
    LearningReservoir,
    AgentAwareCodex,
    PurposeIndexEntry,
    BeliefSignalNode,
    MythicAlignmentMarket,
    SignalEncodingArtifact,
    BeliefNavigationVector,
    ReflectiveFluxIndex,
    RecursiveRitualContract,
    SwarmMythEngineInstance,
    BeliefFeedbackSignal,
    MythicAfterlifeRegistry,
    ContinuityEngineNode,
    ArchetypeMigrationGate,
    ArchetypeGenesisLog,
    MythBloomNode,
    BeliefSeedReplication,
    PublicRitualLogEntry,
    BeliefContinuityThread,
    CodexContributionCeremony,
    NarrativeLightingEngine,
    CinematicUILayer,
    AssistantTutorialScript,
    RitualOnboardingFlow,
    StoryConvergencePath,
    RitualFusionEvent,
    NarrativeCurationTimeline,

    RitualGoalPlanner,
    MythTimelineDirector,
    CodexDecisionFramework,

    DialogueCodexMutationLog,
    NarrativeLightingEngine,
)

from agents.models.coordination import (
    CollaborationThread,
    DelegationStream,
    MythflowInsight,
    MythflowOrchestrationPlan,
    SymbolicCoordinationEngine,
    SymbolicPlanningLattice,
)
from agents.models.insight import (
    InsightHub,
    PerspectiveMergeEvent,
    TimelineStitchLog,
)
from agents.models.identity import (
    SymbolicIdentityCard,
    PersonaTemplate,
    PersonaFusionEvent,
)
from agents.models.cosmology import SwarmCosmology
from agents.models.swarm_balance import (
    PurposeMigrationEvent,
    CognitiveBalanceReport,
    SymbolicResonanceGraph,
)
from agents.models.markets import (
    ForecastingMarketLedger,
    SymbolicFutureContract,
    CosmoEconomicAlignmentMap,
)

from agents.models.storyfield import (
    StoryfieldZone,
    MythPatternCluster,
    IntentHarmonizationSession,
    AgentPlotlineCuration,
)
from assistants.models.assistant import Assistant, AssistantCouncil
from intel_core.serializers import DocumentSerializer


class AgentSerializer(serializers.ModelSerializer):
    trained_documents = DocumentSerializer(many=True, read_only=True)
    parent_assistant_id = serializers.SerializerMethodField()
    parent_assistant_name = serializers.CharField(
        source="parent_assistant.name", read_only=True
    )
    parent_assistant_slug = serializers.CharField(
        source="parent_assistant.slug", read_only=True
    )

    class Meta:
        model = Agent
        fields = [
            "id",
            "parent_assistant_id",
            "parent_assistant_slug",
            "parent_assistant_name",
            "name",
            "slug",
            "description",
            "specialty",
            "agent_type",
            "preferred_llm",
            "execution_mode",
            "tags",
            "skills",
            "verified_skills",
            "strength_score",
            "trained_documents",
            "created_at",
        ]

    def get_parent_assistant_id(self, obj):
        return str(obj.parent_assistant_id) if obj.parent_assistant_id else None


class AgentFeedbackLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentFeedbackLog
        fields = ["id", "task", "feedback_text", "feedback_type", "score", "created_at"]


class AgentClusterSerializer(serializers.ModelSerializer):
    agents = AgentSerializer(many=True, read_only=True)
    project = serializers.SerializerMethodField()
    skill_count = serializers.SerializerMethodField()

    class Meta:
        model = AgentCluster
        fields = ["id", "name", "purpose", "project", "agents", "skill_count"]

    def get_project(self, obj):
        from assistants.serializers import AssistantProjectSummarySerializer

        if obj.project:
            return AssistantProjectSummarySerializer(obj.project).data
        return None

    def get_skill_count(self, obj):
        skills = set()
        for a in obj.agents.all():
            skills.update(a.skills or [])
        return len(skills)


class SwarmMemoryEntrySerializer(serializers.ModelSerializer):

    tags = serializers.SerializerMethodField()

    class Meta:
        model = SwarmMemoryEntry
        fields = [
            "id",
            "title",
            "content",
            "origin",
            "season",
            "tags",
            "created_at",
        ]

    def get_tags(self, obj):
        return list(obj.tags.values_list("name", flat=True))


class SwarmJournalEntrySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = SwarmJournalEntry
        fields = [
            "id",
            "author",
            "author_name",
            "content",
            "tags",
            "is_private",
            "season_tag",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_tags(self, obj):
        return list(obj.tags.values_list("name", flat=True))


class LoreEntrySerializer(serializers.ModelSerializer):
    """Serialize LoreEntry records."""

    associated_event_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SwarmMemoryEntry.objects.all(),
        source="associated_events",
        required=False,
    )
    author_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Assistant.objects.all(),
        source="authors",
        required=False,
    )

    class Meta:
        model = LoreEntry
        fields = [
            "id",
            "title",
            "summary",
            "associated_event_ids",
            "author_ids",
            "is_canon",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LoreEpochSerializer(serializers.ModelSerializer):
    """Serialize LoreEpoch records."""

    class Meta:
        model = LoreEpoch
        fields = ["id", "title", "summary", "created_at"]
        read_only_fields = ["id", "created_at"]


class RetconRequestSerializer(serializers.ModelSerializer):
    """Serialize RetconRequest proposals."""

    class Meta:
        model = RetconRequest
        fields = [
            "id",
            "target_entry",
            "proposed_rewrite",
            "justification",
            "submitted_by",
            "approved",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RealityConsensusVoteSerializer(serializers.ModelSerializer):
    """Serialize council voting records."""

    class Meta:
        model = RealityConsensusVote
        fields = [
            "id",
            "topic",
            "proposed_lore",
            "council",
            "vote_result",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MythDiplomacySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythDiplomacySession
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualCollapseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualCollapseLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class LegacyArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegacyArtifact
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ReincarnationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReincarnationLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ReturnCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnCycle
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class LoreTokenSerializer(serializers.ModelSerializer):
    source_memory_ids = serializers.PrimaryKeyRelatedField(
        queryset=SwarmMemoryEntry.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="source_memories",
    )
    source_memories = SwarmMemoryEntrySerializer(many=True, read_only=True)

    class Meta:
        model = LoreToken
        fields = [
            "id",
            "name",
            "summary",
            "source_memory_ids",
            "source_memories",
            "symbolic_tags",
            "token_type",
            "embedding",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "embedding", "created_at", "source_memories"]


class LoreTokenExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoreTokenExchange
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TokenMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenMarket
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class LoreTokenCraftingRitualSerializer(serializers.ModelSerializer):
    base_memory_ids = serializers.PrimaryKeyRelatedField(
        queryset=SwarmMemoryEntry.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="base_memories",
    )
    base_memories = SwarmMemoryEntrySerializer(many=True, read_only=True)

    class Meta:
        model = LoreTokenCraftingRitual
        fields = "__all__"
        read_only_fields = ["id", "resulting_token", "completed", "created_at"]


class LoreTokenSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoreTokenSignature
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TokenGuildVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenGuildVote
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythRegistryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MythRegistryEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TemporalLoreAnchorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporalLoreAnchor
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualComplianceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualComplianceRecord
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefForkEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefForkEvent
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythCollapseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythCollapseLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MemoryReformationRitualSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryReformationRitual
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class EpistemologyNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpistemologyNode
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefEntanglementLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefEntanglementLink
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CognitiveConstraintProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CognitiveConstraintProfile
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefNegotiationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefNegotiationSession
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ParadoxResolutionAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParadoxResolutionAttempt
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class OntologicalAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OntologicalAuditLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefBiomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefBiome
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicAllianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicAlliance
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DreamPurposeNegotiationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DreamPurposeNegotiation
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BiomeMutationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomeMutationEvent
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SwarmCodexSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwarmCodex
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AgentAwareCodexSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentAwareCodex
        fields = "__all__"
        read_only_fields = ["id", "last_updated"]


class SymbolicLawEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicLawEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualArchiveEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualArchiveEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AssistantPolitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantPolity
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualElection
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class LegacyRoleBindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegacyRoleBinding
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythicArbitrationCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythicArbitrationCase
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TreatyBreachRitualSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatyBreachRitual
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicSanctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicSanction
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SwarmTribunalCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwarmTribunalCase
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RestorativeMemoryActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestorativeMemoryAction
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ReputationRegenerationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReputationRegenerationEvent
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythCycleBindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythCycleBinding
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ResurrectionTemplateSerializer(serializers.ModelSerializer):
    seed_memory_ids = serializers.PrimaryKeyRelatedField(
        queryset=SwarmMemoryEntry.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="seed_memories",
    )
    seed_memories = SwarmMemoryEntrySerializer(many=True, read_only=True)

    class Meta:
        model = ResurrectionTemplate
        fields = "__all__"
        read_only_fields = ["id", "created_at", "seed_memories"]


class SymbolicIdentityCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicIdentityCard
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PersonaTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaTemplate
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PersonaFusionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaFusionEvent
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DialogueCodexMutationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DialogueCodexMutationLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefContinuityRitualSerializer(serializers.ModelSerializer):
    memory_reference_ids = serializers.PrimaryKeyRelatedField(
        queryset=SwarmMemoryEntry.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="memory_reference",
    )
    memory_reference = SwarmMemoryEntrySerializer(many=True, read_only=True)

    class Meta:
        model = BeliefContinuityRitual
        fields = "__all__"
        read_only_fields = ["id", "created_at", "memory_reference"]


class CosmologicalRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CosmologicalRole
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class LegacyTokenVaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegacyTokenVault
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ArchetypeSynchronizationPulseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchetypeSynchronizationPulse
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CreationMythEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CreationMythEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CosmogenesisSimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CosmogenesisSimulation
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythicForecastPulseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythicForecastPulse
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefAtlasSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefAtlasSnapshot
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicWeatherFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicWeatherFront
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CollaborationThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborationThread
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DelegationStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = DelegationStream
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythflowInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythflowInsight
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicCoordinationEngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicCoordinationEngine
        fields = "__all__"
        read_only_fields = ["id", "last_sync"]


class KnowledgeReplicationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeReplicationEvent

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MemoryBroadcastPacketSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryBroadcastPacket

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class LearningReservoirSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningReservoir

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SwarmCosmologySerializer(serializers.ModelSerializer):
    class Meta:
        model = SwarmCosmology
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PurposeIndexEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurposeIndexEntry

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefSignalNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefSignalNode

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythicAlignmentMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythicAlignmentMarket
        fields = "__all__"
        read_only_fields = ["id", "last_updated"]


class SignalEncodingArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalEncodingArtifact

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefNavigationVectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefNavigationVector
        fields = "__all__"
        read_only_fields = ["id", "calculated_at"]


class ReflectiveFluxIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflectiveFluxIndex

        fields = "__all__"
        read_only_fields = ["id", "timestamp"]


class SymbolicResonanceGraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicResonanceGraph
        fields = "__all__"
        read_only_fields = ["id", "generated_at"]


class CognitiveBalanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CognitiveBalanceReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythflowOrchestrationPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythflowOrchestrationPlan
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PurposeMigrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurposeMigrationEvent

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicPlanningLatticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicPlanningLattice
        fields = "__all__"
        read_only_fields = ["id", "last_updated"]


class StoryfieldZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryfieldZone
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythPatternClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythPatternCluster
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class IntentHarmonizationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntentHarmonizationSession
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RecursiveRitualContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecursiveRitualContract

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SwarmMythEngineInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwarmMythEngineInstance

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefFeedbackSignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefFeedbackSignal
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythicAfterlifeRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MythicAfterlifeRegistry

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ContinuityEngineNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContinuityEngineNode
        fields = "__all__"
        read_only_fields = ["id", "last_updated"]


class ArchetypeMigrationGateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchetypeMigrationGate

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ArchetypeGenesisLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchetypeGenesisLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythBloomNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythBloomNode
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefSeedReplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefSeedReplication
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AgentPlotlineCurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentPlotlineCuration
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PublicRitualLogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicRitualLogEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BeliefContinuityThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefContinuityThread
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CodexContributionCeremonySerializer(serializers.ModelSerializer):
    class Meta:
        model = CodexContributionCeremony
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class NarrativeLightingEngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = NarrativeLightingEngine

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CinematicUILayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinematicUILayer
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AssistantTutorialScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantTutorialScript
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualOnboardingFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualOnboardingFlow
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class StoryConvergencePathSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryConvergencePath

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualFusionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualFusionEvent

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class NarrativeCurationTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = NarrativeCurationTimeline
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualGoalPlannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualGoalPlanner
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythTimelineDirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythTimelineDirector
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CodexDecisionFrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodexDecisionFramework
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
