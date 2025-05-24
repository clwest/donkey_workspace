from rest_framework import serializers
from .models import (
    RitualPerformanceMetric,
    RitualReputationScore,
    CodexClauseVote,
    SwarmAlignmentIndex,
)


class RitualPerformanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualPerformanceMetric
        fields = "__all__"


class RitualReputationScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualReputationScore
        fields = "__all__"


class CodexClauseVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodexClauseVote
        fields = "__all__"


class SwarmAlignmentIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwarmAlignmentIndex
        fields = "__all__"
