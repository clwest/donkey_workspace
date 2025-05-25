from rest_framework import serializers
from .models import (
    SimulationConfig,
    SimulationRunLog,
    MythScenarioSimulator,
    RitualInteractionEvent,
    SimulationStateTracker,
    MythflowSession,
    SymbolicDialogueExchange,
    SymbolicDialogueScript,
    MemoryDecisionTreeNode,
    MythflowReflectionLoop,
    CinemythStoryline,
    SceneControlEngine,
    SceneDirectorFrame,
    DreamframeStoryGenerator,
    SimScenarioEngine,
    MultiUserNarrativeLab,
    PurposeLoopCinematicEngine,
    ReflectiveTheaterSession,
    MythflowPlaybackSession,
    SymbolicMilestoneLog,
    PersonalRitualGuide,
    SwarmReflectionThread,
    SwarmReflectionPlaybackLog,
    PromptCascadeLog,
    CascadeNodeLink,
    SimulationClusterStatus,
    SimulationGridNode,
    NarrativeMutationTrace,
)


class SimulationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationConfig
        fields = "__all__"


class SimulationRunLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationRunLog
        fields = "__all__"


class MythScenarioSimulatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythScenarioSimulator
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualInteractionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualInteractionEvent
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SimulationStateTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationStateTracker
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythflowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythflowSession
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicDialogueExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicDialogueExchange
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CinemythStorylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinemythStoryline

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PurposeLoopCinematicEngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurposeLoopCinematicEngine

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ReflectiveTheaterSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflectiveTheaterSession
        fields = "__all__"
        read_only_fields = ["id", "created_at"]



class MythflowPlaybackSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythflowPlaybackSession

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicMilestoneLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicMilestoneLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]



class PersonalRitualGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalRitualGuide
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicDialogueScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicDialogueScript
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MemoryDecisionTreeNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryDecisionTreeNode
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythflowReflectionLoopSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythflowReflectionLoop
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SceneControlEngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SceneControlEngine
        fields = "__all__"
        read_only_fields = ["id", "last_updated"]


class SceneDirectorFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SceneDirectorFrame
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DreamframeStoryGeneratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DreamframeStoryGenerator
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SimScenarioEngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimScenarioEngine
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MultiUserNarrativeLabSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiUserNarrativeLab
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SwarmReflectionThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwarmReflectionThread
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SwarmReflectionPlaybackLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwarmReflectionPlaybackLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PromptCascadeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptCascadeLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CascadeNodeLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CascadeNodeLink
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SimulationClusterStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationClusterStatus
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SimulationGridNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationGridNode
        fields = "__all__"
        read_only_fields = ["id", "created_at"]



class NarrativeMutationTraceSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)

    class Meta:
        model = NarrativeMutationTrace
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CodexSimulationScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodexSimulationScenario
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SwarmClauseDriftMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwarmClauseDriftMetric
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SimulatedBeliefForkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulatedBeliefFork
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RitualDriftObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualDriftObservation
        fields = "__all__"
        read_only_fields = ["id", "observed_at"]


class DriftCorrectionProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriftCorrectionProposal
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythgraphNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythgraphNode
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MythgraphEdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythgraphEdge
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AssistantMythgraphDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantMythgraphDraft
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
