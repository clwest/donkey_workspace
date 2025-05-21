
from rest_framework import serializers
from mcp_core.models import Tag, NarrativeThread, ThreadDiagnosticLog


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "color", "category"]

class NarrativeThreadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    related_memory_previews = serializers.SerializerMethodField()
    origin_memory_preview = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField()

    class Meta:
        model = NarrativeThread
        fields = [
            "id",
            "title",
            "summary",
            "tags",
            "created_by",
            "created_at",
            "continuity_score",
            "last_diagnostic_run",
            "origin_memory",
            "origin_memory_preview",
            "related_memory_previews",
        ]

    def get_origin_memory_preview(self, obj):
        if obj.origin_memory:
            return {
                "id": str(obj.origin_memory.id),
                "preview": obj.origin_memory.content[:200],
                "created_at": obj.origin_memory.created_at,
            }
        return None

    def get_related_memory_previews(self, obj):
        return [
            {
                "id": str(mem.id),
                "preview": mem.content[:200],
                "created_at": mem.created_at,
            }
            for mem in obj.related_memories.all().order_by("-created_at")
        ]


class ThreadDiagnosticLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadDiagnosticLog
        fields = ["id", "score", "summary", "created_at"]
