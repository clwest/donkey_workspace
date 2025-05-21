from rest_framework import serializers
from agents.models import (
    Agent,
    AgentFeedbackLog,
    AgentCluster,
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
)
from assistants.models import Assistant, AssistantCouncil
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
