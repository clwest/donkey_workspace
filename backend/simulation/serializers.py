from rest_framework import serializers
from .models import (
    SimulationConfig,
    SimulationRunLog,
    MythScenarioSimulator,
    RitualInteractionEvent,
    SimulationStateTracker,
    MythflowSession,
    SymbolicDialogueExchange,

    MemoryProjectionFrame,
    BeliefNarrativeWalkthrough,
    DreamframePlaybackSegment,

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



class MemoryProjectionFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryProjectionFrame

        fields = "__all__"
        read_only_fields = ["id", "created_at"]



class BeliefNarrativeWalkthroughSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefNarrativeWalkthrough

        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DreamframePlaybackSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DreamframePlaybackSegment

        fields = "__all__"
        read_only_fields = ["id", "created_at"]

