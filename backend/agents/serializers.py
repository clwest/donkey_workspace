from rest_framework import serializers
from agents.models import (
    Agent,
    AgentFeedbackLog,
    AgentCluster,
    SwarmMemoryEntry,
    LoreEntry,
    RetconRequest,
    RealityConsensusVote,
    MythDiplomacySession,
    RitualCollapseLog,
)
from intel_core.serializers import DocumentSerializer


class AgentSerializer(serializers.ModelSerializer):
    trained_documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Agent
        fields = [
            "id",
            "assistant",
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
        from assistants.serializers import AssistantProjectSerializer

        if obj.project:
            return AssistantProjectSerializer(obj.project).data
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


class LoreEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoreEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RetconRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetconRequest
        fields = "__all__"
        read_only_fields = ["id", "approved", "created_at"]


class RealityConsensusVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealityConsensusVote
        fields = "__all__"
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
