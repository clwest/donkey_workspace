from rest_framework import serializers
from django.db.models import Q
from intel_core.models import DocumentChunk
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
    GlossaryRetryLog,
    AnchorConvergenceLog,
    AnchorReinforcementLog,
    RAGGroundingLog,
    RAGPlaybackLog,
    RAGDiagnosticLog,
    GlossaryKeeperLog,
)

from assistants.models.thoughts import AssistantThoughtLog
from agents.serializers import AgentSerializer
from mcp_core.serializers_tags import NarrativeThreadSerializer
from mcp_core.serializers_tags import TagSerializer


class SimulatedMemoryForkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulatedMemoryFork
        fields = "__all__"


class MemoryEntryFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryEntry
        fields = [
            "id",
            "assistant",
            "source_user",
            "event",
            "rating",
            "created_at",
        ]
        read_only_fields = ["id", "assistant", "source_user", "created_at"]


class MemoryEntrySerializer(serializers.ModelSerializer):
    linked_thought = serializers.SerializerMethodField()
    narrative_thread = NarrativeThreadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    content_preview = serializers.CharField(read_only=True)
    triggered_by = serializers.CharField(read_only=True)
    delegation_event_id = serializers.SerializerMethodField()
    assistant_name = serializers.SerializerMethodField()
    assistant_id = serializers.SerializerMethodField()
    assistant_slug = serializers.SerializerMethodField()
    parent_assistant_name = serializers.SerializerMethodField()
    is_delegated = serializers.SerializerMethodField()
    simulated_forks = SimulatedMemoryForkSerializer(many=True, read_only=True)
    linked_agents = AgentSerializer(many=True, read_only=True)
    anchor_slug = serializers.SlugField(source="anchor.slug", read_only=True)
    positive_feedback_count = serializers.SerializerMethodField()
    negative_feedback_count = serializers.SerializerMethodField()

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
            "is_active",
            "was_used_in_chat",
            "created_at",
            "is_demo",
            "linked_thought",
            "content_preview",
            "triggered_by",
            "is_conversation",
            "session_id",
            "rating",
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
            "assistant_slug",
            "parent_assistant_name",
            "is_delegated",
            "linked_agents",
            "simulated_forks",
            "positive_feedback_count",
            "negative_feedback_count",
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

    def validate_event(self, value):
        import bleach

        cleaned = bleach.clean(value, strip=True)
        if len(cleaned) > 10000:
            raise serializers.ValidationError("event too long")
        return cleaned

    def validate_summary(self, value):
        import bleach

        return bleach.clean(value, strip=True)

    def get_delegation_event_id(self, obj):
        if hasattr(obj, "delegation_event_id"):
            return str(obj.delegation_event_id) if obj.delegation_event_id else None
        event = obj.delegation_events.first()
        return str(event.id) if event else None

    def get_assistant_name(self, obj):
        return getattr(obj.assistant, "name", None)

    def get_assistant_id(self, obj):
        return str(obj.assistant_id) if obj.assistant_id else None

    def get_assistant_slug(self, obj):
        return getattr(obj.assistant, "slug", None)

    def get_parent_assistant_name(self, obj):
        if obj.assistant and obj.assistant.parent_assistant:
            return obj.assistant.parent_assistant.name
        return None

    def get_is_delegated(self, obj):
        if hasattr(obj, "is_delegated"):
            return obj.is_delegated
        return bool(obj.assistant and obj.assistant.parent_assistant)

    def get_positive_feedback_count(self, obj):
        """Return count of positive feedback items for this memory."""
        return obj.feedback.filter(rating="positive").count()

    def get_negative_feedback_count(self, obj):
        """Return count of negative feedback items for this memory."""
        return obj.feedback.filter(rating="negative").count()


class MemoryFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryFeedback
        fields = [
            "id",
            "memory",
            "project",
            "thought_log",
            "context_hint",
            "suggestion",
            "explanation",
            "mutation_style",
            "status",
            "rating",
            "submitted_by",
            "created_at",
        ]


class MemoryChainSerializer(serializers.ModelSerializer):

    class Meta:
        model = MemoryChain
        fields = "__all__"


class MemoryEntrySlimSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing assistant memories."""

    tags = TagSerializer(many=True, read_only=True)
    token_count = serializers.SerializerMethodField()
    content_preview = serializers.CharField(read_only=True)
    triggered_by = serializers.CharField(read_only=True)
    positive_feedback_count = serializers.SerializerMethodField()
    negative_feedback_count = serializers.SerializerMethodField()

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
            "is_active",
            "was_used_in_chat",
            "positive_feedback_count",
            "negative_feedback_count",
        ]

    def get_token_count(self, obj):
        from prompts.utils.token_helpers import count_tokens

        text = obj.summary or obj.event or ""
        try:
            return count_tokens(text)
        except Exception:
            return len(text.split())

    def get_positive_feedback_count(self, obj):
        return obj.feedback.filter(rating="positive").count()

    def get_negative_feedback_count(self, obj):
        return obj.feedback.filter(rating="negative").count()


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
    reinforced_by = serializers.SlugRelatedField(
        slug_field="slug", many=True, read_only=True
    )
    chunks_count = serializers.SerializerMethodField()
    retagged_count = serializers.SerializerMethodField()
    first_used_at = serializers.SerializerMethodField()
    total_matches = serializers.SerializerMethodField()
    mutation_score = serializers.SerializerMethodField()
    fallback_count = serializers.SerializerMethodField()
    glossary_boost = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    reinforcement_count = serializers.SerializerMethodField()
    last_used_at = serializers.SerializerMethodField()
    drift_score = serializers.SerializerMethodField()

    class Meta:
        model = SymbolicMemoryAnchor
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def get_chunks_count(self, obj):
        return (
            DocumentChunk.objects.filter(
                Q(anchor=obj) | Q(matched_anchors__contains=[obj.slug])
            )
            .distinct()
            .count()
        )

    def get_retagged_count(self, obj):
        return (
            DocumentChunk.objects.filter(matched_anchors__contains=[obj.slug])
            .exclude(anchor=obj)
            .count()
        )

    def get_first_used_at(self, obj):
        chunk = (
            DocumentChunk.objects.filter(
                Q(anchor=obj) | Q(matched_anchors__contains=[obj.slug])
            )
            .order_by("created_at")
            .first()
        )
        return chunk.created_at if chunk else None

    def get_total_matches(self, obj):
        return self.get_chunks_count(obj)

    def _conv_stats(self, obj):
        if not hasattr(obj, "_conv_cache"):
            from .services.convergence import calculate_convergence_stats

            obj._conv_cache = calculate_convergence_stats(obj)
        return obj._conv_cache

    def get_mutation_score(self, obj):
        return self._conv_stats(obj).get("mutation_score")

    def get_fallback_count(self, obj):
        return self._conv_stats(obj).get("fallback_count")

    def get_glossary_boost(self, obj):
        return self._conv_stats(obj).get("glossary_boost")

    def get_last_updated(self, obj):
        return self._conv_stats(obj).get("last_updated")

    def get_reinforcement_count(self, obj):
        return obj.reinforcement_logs.count()

    def get_last_used_at(self, obj):
        return obj.last_used_in_reflection

    def get_drift_score(self, obj):
        total = obj.chunks.count()
        drifted = obj.chunks.filter(is_drifting=True).count()
        return round(drifted / total, 2) if total else 0.0


class MemoryMergeSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryMergeSuggestion
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class GlossaryRetryLogSerializer(serializers.ModelSerializer):
    anchor_label = serializers.CharField(source="anchor.label", read_only=True)

    class Meta:
        model = GlossaryRetryLog
        fields = [
            "id",
            "anchor",
            "anchor_slug",
            "question",
            "first_response",
            "retry_response",
            "glossary_chunk_ids",
            "guidance_injected",
            "retried",
            "retry_type",
            "score_diff",
            "created_at",
            "anchor_label",
        ]
        read_only_fields = ["id", "created_at"]


class AnchorConvergenceLogSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)
    memory_summary = serializers.CharField(source="memory.summary", read_only=True)
    anchor_label = serializers.CharField(source="anchor.label", read_only=True)
    anchor_slug = serializers.CharField(source="anchor.slug", read_only=True)

    class Meta:
        model = AnchorConvergenceLog
        fields = [
            "id",
            "anchor",
            "assistant",
            "memory",
            "guidance_used",
            "retried",
            "final_score",
            "created_at",
            "assistant_name",
            "memory_summary",
            "anchor_label",
            "anchor_slug",
        ]
        read_only_fields = ["id", "created_at"]


class AnchorReinforcementLogSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)
    anchor_label = serializers.CharField(source="anchor.label", read_only=True)

    class Meta:
        model = AnchorReinforcementLog
        fields = [
            "id",
            "anchor",
            "assistant",
            "memory",
            "reason",
            "score",
            "created_at",
            "assistant_name",
            "anchor_label",
        ]
        read_only_fields = ["id", "created_at"]


class RAGGroundingLogSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source="assistant.name", read_only=True)
    glossary_boost = serializers.FloatField(
        source="glossary_boost_applied", read_only=True
    )
    matched_chunk_ids = serializers.SerializerMethodField()

    class Meta:
        model = RAGGroundingLog
        fields = [
            "id",
            "assistant",
            "assistant_name",
            "query",
            "used_chunk_ids",
            "matched_chunk_ids",
            "fallback_triggered",
            "fallback_reason",
            "expected_anchor",
            "glossary_hits",
            "glossary_misses",
            "retrieval_score",
            "corrected_score",
            "raw_score",
            "adjusted_score",
            "glossary_boost",
            "boosted_from_reflection",
            "reflection_boost_score",
            "glossary_boost_type",
            "fallback_threshold_used",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_matched_chunk_ids(self, obj):
        return obj.used_chunk_ids or []


class RAGPlaybackLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGPlaybackLog
        fields = [
            "id",
            "assistant",
            "query",
            "memory_context",
            "chunks",
            "demo_session_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DriftHeatmapEntrySerializer(serializers.Serializer):
    reflection_id = serializers.UUIDField()
    anchor_slug = serializers.CharField()
    anchor_label = serializers.CharField()
    drift_score = serializers.FloatField()
    timestamp = serializers.DateTimeField(allow_null=True)
    milestone_title = serializers.CharField(allow_null=True, required=False)


class GlossaryKeeperLogSerializer(serializers.ModelSerializer):
    """Serializer for GlossaryKeeperLog entries."""

    anchor_slug = serializers.CharField(source="anchor.slug", read_only=True)
    anchor_label = serializers.CharField(source="anchor.label", read_only=True)
    assistant_slug = serializers.CharField(source="assistant.slug", read_only=True)
    memory_id = serializers.SerializerMethodField()
    suggested_label = serializers.CharField(
        source="anchor.suggested_label", read_only=True
    )
    anchor_drift = serializers.SerializerMethodField()
    fallback_score = serializers.FloatField(
        source="anchor.fallback_score", read_only=True
    )
    glossary_state = serializers.CharField(
        source="anchor.acquisition_stage", read_only=True
    )

    class Meta:
        model = GlossaryKeeperLog
        fields = [
            "id",
            "anchor",
            "assistant",
            "action_taken",
            "score_before",
            "score_after",
            "notes",
            "timestamp",
            "anchor_slug",
            "anchor_label",
            "assistant_slug",
            "memory_id",
            "suggested_label",
            "anchor_drift",
            "fallback_score",
            "glossary_state",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_memory_id(self, obj):
        return getattr(obj, "memory_id", None)

    def get_anchor_drift(self, obj):
        anchor = obj.anchor
        total = anchor.chunks.count()
        drifted = anchor.chunks.filter(is_drifting=True).count()
        return round(drifted / total, 2) if total else 0.0

class RAGDiagnosticLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGDiagnosticLog
        fields = [
            "id",
            "assistant",
            "query_text",
            "timestamp",
            "retrieved_chunks",
            "fallback_triggered",
            "glossary_matches",
            "used_memory_context",
            "reflection_boosts_applied",
            "confidence_score_avg",
            "token_usage",
            "explanation_text",
        ]
        read_only_fields = ["id", "timestamp"]

