from rest_framework import serializers
from .models import (
    SimulationConfig,
    SimulationRunLog,
    MythScenarioSimulator,
    RitualInteractionEvent,
    SimulationStateTracker,
    MythflowSession,
    SymbolicDialogueExchange,
    BeliefNarrativeEngineInstance,
    SymbolicAuthorityTransferLog,
    MemoryCinematicFragment,
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


class BeliefNarrativeEngineInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeliefNarrativeEngineInstance
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SymbolicAuthorityTransferLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicAuthorityTransferLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class MemoryCinematicFragmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryCinematicFragment
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
