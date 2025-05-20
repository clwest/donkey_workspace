"""Serializers that convert project-related models to JSON for the API."""

from rest_framework import serializers
from .models import (
    Project,
    ProjectTask,
    ProjectMilestone,
    ProjectMemoryLink,
    ProjectType,
    ProjectStatus,
    TaskStatus,
    MilestoneStatus,
)
from story.serializers import StorySerializer
from images.serializers import ImageSerializer

from tts.serializers import StoryAudioSerializer
from mcp_core.models import DevDoc
from mcp_core.serializers_tags import NarrativeThreadSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Detailed representation of a project with related media and assistant."""
    stories = StorySerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True, source="image_set")
    assistant = serializers.SerializerMethodField()
    tts_audios = serializers.SerializerMethodField()
    narrative_thread = NarrativeThreadSerializer(read_only=True)
    team = serializers.SerializerMethodField()
    team_chain = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

    def get_assistant(self, obj):
        from assistants.serializers import AssistantSerializer  # 🧙 lazy import here

        if obj.assistant:
            return AssistantSerializer(obj.assistant).data
        return None

    def get_tts_audios(self, obj):
        from tts.models import StoryAudio

        return StoryAudioSerializer(
            StoryAudio.objects.filter(story__project=obj), many=True
        ).data

    def get_open_task_count(self, obj):
        return obj.open_task_count()

    def get_completed_task_count(self, obj):
        return obj.completed_task_count()

    def get_completion_percent(self, obj):
        return obj.completion_percent()

    def get_team(self, obj):
        from assistants.serializers import AssistantSerializer
        return AssistantSerializer(obj.team.all(), many=True).data


class ProjectTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectTask
        fields = ["id", "title", "notes", "status", "priority", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectMilestoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectMilestone
        fields = [
            "id",
            "project",
            "title",
            "description",
            "due_date",
            "status",
            "is_completed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProjectMemoryLinkSerializer(serializers.ModelSerializer):
    """Represents links between projects and memory entries."""
    class Meta:
        model = ProjectMemoryLink
        fields = ["id", "project", "memory", "reason", "linked_at"]
        read_only_fields = ["id", "linked_at"]


class DevDocPreviewSerializer(serializers.ModelSerializer):
    """Lightweight serializer for previewing DevDocs."""
    class Meta:
        model = DevDoc
        fields = ["id", "title", "slug", "content"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Full project representation including associated DevDocs."""
    dev_docs = DevDocPreviewSerializer(many=True, read_only=True)
    narrative_thread = NarrativeThreadSerializer(read_only=True)


    class Meta:
        model = Project
        fields = "__all__"

    def get_open_task_count(self, obj):
        return obj.open_task_count()

    def get_completed_task_count(self, obj):
        return obj.completed_task_count()

    def get_completion_percent(self, obj):
        return obj.completion_percent()
