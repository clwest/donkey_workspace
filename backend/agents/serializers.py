from rest_framework import serializers
from agents.models import Agent, AgentFeedbackLog, AgentCluster
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


from assistants.serializers import AssistantProjectSerializer

class AgentClusterSerializer(serializers.ModelSerializer):
    agents = AgentSerializer(many=True, read_only=True)
    project = AssistantProjectSerializer(read_only=True)
    skill_count = serializers.SerializerMethodField()

    class Meta:
        model = AgentCluster
        fields = ["id", "name", "purpose", "project", "agents", "skill_count"]

    def get_skill_count(self, obj):
        skills = set()
        for a in obj.agents.all():
            skills.update(a.skills or [])
        return len(skills)
