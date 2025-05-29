from rest_framework import serializers
from .models import (
    MemoryEntry,
    MemoryFeedback,
    MemoryChain,
    SimulatedMemoryFork,
    SharedMemoryPool,
    SharedMemoryEntry,
    BraidedMemoryStrand,
    ContinuityAnchorPoint,
    SymbolicMemoryAnchor,
    MemoryMergeSuggestion,
)

from assistants.models.thoughts import AssistantThoughtLog
from agents.serializers import AgentSerializer
from mcp_core.serializers_tags import NarrativeThreadSerializer
from mcp_core.serializers_tags import TagSerializer


class SimulatedMemoryForkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulatedMemoryFork
        fields = "__all__"


class MemoryEntrySerializer(serializers.ModelSerializer):
    linked_thought = serializers.SerializerMethodField()
    narrative_thread = NarrativeThreadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    content_preview = serializers.CharField(source="content_preview", read_only=True)
    triggered_by = serializers.CharField(read_only=True)
    delegation_event_id = serializers.SerializerMethodField()
    assistant_name = serializers.SerializerMethodField()
    assistant_id = serializers.SerializerMethodField()
    parent_assistant_name = serializers.SerializerMethodField()
    is_delegated = serializers.SerializerMethodField()
    simulated_forks = SimulatedMemoryForkSerializer(many=True, read_only=True)
    linked_agents = AgentSerializer(many=True, read_only=True)
    anchor_slug = serializers.SlugField(source="anchor.slug", read_only=True)

    class Meta:
        model = MemoryEntry
        fields = [
            "id",
            "event",
            "summary",
            "title",
            "timestamp",
            "emotion",
            "importance",
            "tags",
            "voice_clip",
            "created_at",
            "linked_thought",
            "content_preview",
            "triggered_by",
            "is_conversation",
            "session_id",
            "full_transcript",
            "narrative_thread",
            "source_name",
            "parent_memory",
            "type",
            "tool_response",
            "is_bookmarked",
            "bookmark_label",
            "symbolic_change",
            "related_campaign",
            "anchor_slug",
            "delegation_event_id",
            "assistant_name",
            "assistant_id",
            "parent_assistant_name",
            "is_delegated",
            "linked_agents",
            "simulated_forks",
        ]

    def get_source_name(self, obj):
        return obj.source_name

    def get_linked_thought(self, obj):
        thought = obj.linked_thought
        if not thought or not thought.assistant:
            return None
        return {
            "id": str(thought.id),  # 👈 this is what your frontend expects
            "assistant_name": thought.assistant.name,
            "assistant_slug": thought.assistant.slug,
            "preview": (
                thought.thought[:120] + "..."
                if len(thought.thought) > 120
                else thought.thought
            ),
        }

    def get_delegation_event_id(self, obj):
        if hasattr(obj, "delegation_event_id"):
            return str(obj.delegation_event_id) if obj.delegation_event_id else None
        event = obj.delegation_events.first()
        return str(event.id) if event else None

    def get_assistant_name(self, obj):
        return getattr(obj.assistant, "name", None)

    def get_assistant_id(self, obj):
        return str(obj.assistant_id) if obj.assistant_id else None

    def get_parent_assistant_name(self, obj):
        if obj.assistant and obj.assistant.parent_assistant:
            return obj.assistant.parent_assistant.name
        return None

    def get_is_delegated(self, obj):
        if hasattr(obj, "is_delegated"):
            return obj.is_delegated
        return bool(obj.assistant and obj.assistant.parent_assistant)


class MemoryFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryFeedback
        fields = "__all__"


class MemoryChainSerializer(serializers.ModelSerializer):

    class Meta:
        model = MemoryChain
        fields = "__all__"


class MemoryEntrySlimSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing assistant memories."""

    tags = TagSerializer(many=True, read_only=True)
    token_count = serializers.SerializerMethodField()
    content_preview = serializers.CharField(source="content_preview", read_only=True)
    triggered_by = serializers.CharField(read_only=True)

    class Meta:
        model = MemoryEntry
        fields = [
            "id",
            "content_preview",
            "triggered_by",
            "summary",
            "title",
            "tags",
            "type",
            "token_count",
            "created_at",
            "parent_memory",
            "is_bookmarked",
            "bookmark_label",
            "symbolic_change",
            "related_campaign",
        ]

    def get_token_count(self, obj):
        from prompts.utils.token_helpers import count_tokens

        text = obj.summary or obj.event or ""
        try:
            return count_tokens(text)
        except Exception:
            return len(text.split())


class PrioritizedMemorySerializer(MemoryEntrySlimSerializer):
    """Serializer with extra fields for prioritized listing."""

    feedback_count = serializers.IntegerField(read_only=True)

    class Meta(MemoryEntrySlimSerializer.Meta):
        fields = MemoryEntrySlimSerializer.Meta.fields + [
            "importance",
            "relevance_score",
            "feedback_count",
        ]


class SharedMemoryPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedMemoryPool
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class SharedMemoryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedMemoryEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class NarrativeThreadOverviewSerializer(NarrativeThreadSerializer):
    """Lightweight serializer for thread overview dashboard."""

    class Meta(NarrativeThreadSerializer.Meta):
        fields = [
            "id",
            "title",
            "summary",
            "tags",
            "created_at",
            "avg_mood",
            "last_updated",
            "reflection_count",
            "continuity_score",
            "gaps_detected",
        ]


class BraidedMemoryStrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = BraidedMemoryStrand
        fields = "__all__"


class ContinuityAnchorPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContinuityAnchorPoint
        fields = "__all__"


class SymbolicMemoryAnchorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolicMemoryAnchor
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

class MemoryMergeSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryMergeSuggestion
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

