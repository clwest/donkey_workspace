from rest_framework import serializers

from mcp_core.models import Tag, NarrativeThread
from mcp_core.models import ThreadObjectiveReflection


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "color", "category"]


class ThreadObjectiveReflectionSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    class Meta:
        model = ThreadObjectiveReflection
        fields = ["id", "thread", "thought", "created_by", "created_at"]


class NarrativeThreadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    related_memory_previews = serializers.SerializerMethodField()
    origin_memory_preview = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField()
    objective_reflections = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()
    reflection_count = serializers.SerializerMethodField()
    gaps_detected = serializers.SerializerMethodField()
    potential_link_suggestions = serializers.SerializerMethodField()
    recent_moods = serializers.SerializerMethodField()

    class Meta:
        model = NarrativeThread
        fields = [
            "id",
            "title",
            "summary",
            "long_term_objective",
            "milestones",
            "tags",
            "created_by",
            "created_at",
            "mood_at_creation",
            "avg_mood",
              "continuity_summary",
              "continuity_score",
              "last_diagnostic_run",
              "last_refocus_prompt",
              "last_updated",
              "reflection_count",
            "origin_memory",
            "origin_memory_preview",
            "related_memory_previews",
            "objective_reflections",
            "gaps_detected",
            "potential_link_suggestions",
            "recent_moods",
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

    def get_last_updated(self, obj):
        from django.db.models import Max
        from django.utils import timezone

        mem_time = obj.thread_memories.aggregate(Max("created_at"))["created_at__max"]
        thought_time = obj.thoughts.aggregate(Max("created_at"))["created_at__max"]
        times = [t for t in [mem_time, thought_time] if t]
        return max(times) if times else obj.created_at

    def get_reflection_count(self, obj):
        return obj.thoughts.filter(thought_type="reflection").count()

    def get_gaps_detected(self, obj):
        from django.utils import timezone

        gaps = []
        last = self.get_last_updated(obj)
        if last and (timezone.now() - last).days > 7:
            gaps.append("inactive")
        if self.get_reflection_count(obj) == 0:
            gaps.append("missing_reflections")
        return gaps


def get_potential_link_suggestions(self, obj):
    return getattr(obj, "_link_suggestions", [])

def get_objective_reflections(self, obj):
    return [
        {
            "id": str(r.id),
            "thought": r.thought[:200],
            "created_at": r.created_at,
        }
        for r in obj.objective_reflections.all().order_by("-created_at")
    ]

    def get_recent_moods(self, obj):
        logs = obj.thoughts.order_by("-created_at")[:10]
        return [
            {
                "mood": t.mood,
                "created_at": t.created_at,
            }
            for t in logs
            if t.mood

    def get_potential_link_suggestions(self, obj):
        return getattr(obj, "_link_suggestions", [])

    def get_objective_reflections(self, obj):
        return [
            {
                "id": str(r.id),
                "thought": r.thought[:200],
                "created_at": r.created_at,
            }
            for r in obj.objective_reflections.all().order_by("-created_at")

        ]
