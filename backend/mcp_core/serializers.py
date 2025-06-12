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
from assistants.models.assistant import Assistant
from assistants.models.reflection import AssistantReflectionLog

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
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    raw_summary = serializers.CharField(
        source="raw_prompt", allow_null=True, read_only=True
    )
    related_anchors = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="slug",
    )

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
    source_assistant_slug = serializers.SerializerMethodField()
    source_assistant_name = serializers.SerializerMethodField()
    related_docs = DevDocSerializer(many=True, read_only=True)

    class Meta:
        model = GroupedDevDocReflection
        fields = [
            "id",
            "summary",
            "raw_json",
            "created_at",
            "tags",
            "source_assistant_slug",
            "source_assistant_name",
            "related_docs",
        ]

    def get_source_assistant_slug(self, obj):
        return getattr(obj.source_assistant, "slug", None)

    def get_source_assistant_name(self, obj):
        if obj.source_assistant:
            return obj.source_assistant.name
        return None
