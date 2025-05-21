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
    AssistantCivilization,
    LoreInheritanceLine,
    MythSimulationArena,
)
from assistants.models import Assistant, AssistantCouncil
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


class AssistantCivilizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantCivilization
        fields = ["id", "name", "description", "belief_system", "created_at"]
        read_only_fields = ["id", "created_at"]


class LoreInheritanceLineSerializer(serializers.ModelSerializer):
    source_title = serializers.CharField(source="source.title", read_only=True)
    descendant_title = serializers.CharField(source="descendant.title", read_only=True)

    class Meta:
        model = LoreInheritanceLine
        fields = [
            "id",
            "source",
            "descendant",
            "source_title",
            "descendant_title",
            "traits_passed",
            "mutation_summary",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MythSimulationArenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythSimulationArena
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
