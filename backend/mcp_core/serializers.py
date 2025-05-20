from rest_framework import serializers
from .models import (
    MemoryContext,
    Plan,
    Task,
    DevDoc,
    Fault,
    ActionLog,
    
    NarrativeThread,
    GroupedDevDocReflection,
)
from mcp_core.serializers_tags import TagSerializer
from assistants.models import Assistant, AssistantReflectionLog
from assistants.serializers import AssistantSerializer
from prompts.models import PromptUsageTemplate


class MemoryContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryContext
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class FaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fault
        fields = "__all__"


class ActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionLog
        fields = "__all__"


class ReflectionLogSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    raw_summary = serializers.CharField(source="raw_prompt", allow_null=True, read_only=True)

    class Meta:
        model = AssistantReflectionLog  # or whatever model you're using
        fields = "__all__"


from mcp_core.models import PromptUsageLog


class PromptUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptUsageLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]




class DevDocSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    linked_assistants = serializers.SerializerMethodField()

    class Meta:
        model = DevDoc
        fields = [
            "id",
            "uuid",
            "title",
            "slug",
            "content",
            "reflected_at",
            "created_at",
            "source_file",
            "tags",
            "linked_assistants",
        ]
        read_only_fields = ["reflected_at"]
    def get_linked_assistants(self, obj):
        return [
            {"id": a.id, "name": a.name, "slug": a.slug}
            for a in obj.linked_assistants.all()
        ]

class GroupedDevDocReflectionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    source_assistant = AssistantSerializer(read_only=True)
    related_docs = DevDocSerializer(many=True, read_only=True)

    class Meta:
        model = GroupedDevDocReflection
        fields = [
            "id",
            "summary",
            "raw_json",
            "created_at",
            "tags",
            "source_assistant",
            "related_docs",
        ]


