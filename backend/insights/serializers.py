from rest_framework import serializers
from .models import SymbolicAgentInsightLog, AssistantInsightLog


class SymbolicAgentInsightLogSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source="agent.name", read_only=True)
    document_title = serializers.CharField(source="document.title", read_only=True)

    class Meta:
        model = SymbolicAgentInsightLog
        fields = [
            "id",
            "agent",
            "agent_name",
            "document",
            "document_title",
            "symbol",
            "conflict_score",
            "resolution_method",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssistantInsightLogSerializer(serializers.ModelSerializer):
    assistant_slug = serializers.CharField(source="assistant.slug", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AssistantInsightLog
        fields = [
            "id",
            "assistant",
            "assistant_slug",
            "user",
            "user_name",
            "summary",
            "tags",
            "proposed_prompt",
            "accepted",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
