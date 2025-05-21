from rest_framework import serializers
from agents.models import Agent, AgentFeedbackLog

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            "id",
            "assistant",
            "name",
            "slug",
            "description",
            "preferred_llm",
            "execution_mode",
            "created_at",
        ]


class AgentFeedbackLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentFeedbackLog
        fields = ["id", "task", "feedback_text", "feedback_type", "score", "created_at"]
