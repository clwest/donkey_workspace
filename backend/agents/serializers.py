from rest_framework import serializers
from agents.models import Agent

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
            "execution_style",
            "created_at",
        ]