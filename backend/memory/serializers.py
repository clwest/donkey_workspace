from rest_framework import serializers
from .models import MemoryEntry, MemoryFeedback, MemoryChain

from assistants.models import AssistantThoughtLog
from assistants.serializers import AssistantSerializer  # if needed
from mcp_core.serializers_tags import NarrativeThreadSerializer
from mcp_core.serializers_tags import TagSerializer

class MemoryEntrySerializer(serializers.ModelSerializer):
    linked_thought = serializers.SerializerMethodField()
    narrative_thread = NarrativeThreadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = MemoryEntry
        fields = [
            "id",
            "event",
            "timestamp",
            "emotion",
            "importance",
            "tags",
            "voice_clip",
            "created_at",
            "linked_thought",
            "is_conversation",
            "session_id",
            "full_transcript",
            "narrative_thread",
            "source_name",
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

    class Meta:
        model = MemoryEntry
        fields = ["id", "summary", "tags", "token_count", "created_at"]

    def get_token_count(self, obj):
        from prompts.utils.token_helpers import count_tokens

        text = obj.summary or obj.event or ""
        try:
            return count_tokens(text)
        except Exception:
            return len(text.split())
