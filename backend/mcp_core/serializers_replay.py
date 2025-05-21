from rest_framework import serializers
from memory.models import MemoryEntry
from assistants.models import AssistantThoughtLog, AssistantReflectionLog


class ThreadReplayItemSerializer(serializers.Serializer):
    """Normalize memory, thought, and reflection logs for thread replay."""

    type = serializers.CharField()
    id = serializers.CharField()
    created_at = serializers.DateTimeField()
    content = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    tone = serializers.CharField(required=False, allow_null=True)
    insight = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, obj):
        with_context = self.context.get("with_context")
        data = {
            "type": None,
            "id": str(obj.id),
            "created_at": obj.created_at,
            "content": "",
            "tags": [],
            "tone": None,
            "insight": None,
        }
        if isinstance(obj, MemoryEntry):
            data.update(
                {
                    "type": "memory",
                    "content": obj.event,
                    "tags": [t.name for t in obj.tags.all()],
                    "tone": obj.emotion,
                }
            )
            thread = obj.thread
        elif isinstance(obj, AssistantThoughtLog):
            data.update(
                {
                    "type": "thought",
                    "content": obj.thought,
                    "tags": [t.name for t in obj.tags.all()],
                    "tone": obj.mood,
                }
            )
            thread = obj.narrative_thread
        elif isinstance(obj, AssistantReflectionLog):
            data.update(
                {
                    "type": "reflection",
                    "content": obj.summary,
                    "tags": [t.name for t in obj.tags.all()],
                    "tone": obj.mood,
                    "insight": obj.insights,
                }
            )
            thread = obj.linked_memory.thread if obj.linked_memory else None
        else:
            return super().to_representation(obj)

        if with_context and thread:
            before_mem = (
                MemoryEntry.objects.filter(thread=thread, created_at__lt=obj.created_at)
                .order_by("-created_at")
                .first()
            )
            after_mem = (
                MemoryEntry.objects.filter(thread=thread, created_at__gt=obj.created_at)
                .order_by("created_at")
                .first()
            )
            data["context"] = {
                "before": before_mem.event if before_mem else None,
                "after": after_mem.event if after_mem else None,
            }
        return data
