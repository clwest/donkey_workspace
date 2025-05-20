from django.contrib import admin
from .models import (
    Assistant,
    AssistantThoughtLog,
    AssistantProject,
    AssistantObjective,
    AssistantNextAction,
    AssistantReflectionLog,
    ChatSession,
    DelegationEvent,
    DelegationStrategy,
    SessionHandoff,
    AssistantMemoryChain,
    SpecializationDriftLog,
)
from memory.models import MemoryEntry
from mcp_core.models import Tag


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "specialty",
        "preferred_model",
        "is_active",
        "is_demo",
        "created_at",
    )
    search_fields = ("name", "slug", "specialty")
    list_filter = ("preferred_model", "is_demo", "is_active", "created_at")
    readonly_fields = ("created_at", "slug")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "specialty", "avatar")}),
        (
            "Behavior",
            {
                "fields": (
                    "system_prompt",
                    "tone",
                    "personality",
                    "preferred_model",
                    "memory_mode",
                    "thinking_style",
                )
            },
        ),
        ("Meta", {"fields": ("is_active", "is_demo", "created_by", "created_at")}),
    )


@admin.register(AssistantThoughtLog)
class AssistantThoughtLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project",
        "created_at",
        "updated_at",
        "thought_type",
        "feedback",
    )
    search_fields = ("thought", "project__title")
    list_filter = ("created_at", "updated_at", "thought_type", "feedback")
    filter_horizontal = ("tags",)

    def short_thought(self, obj):
        return obj.thought[:80] + "…" if len(obj.thought) > 80 else obj.thought

    short_thought.short_description = "Thought Preview"


@admin.register(MemoryEntry)
class MemoryEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assistant",
        "related_project",
        "importance",
        "timestamp",
        "tag_list",
    )
    list_filter = ("assistant", "importance", "timestamp")
    search_fields = ("full_transcript", "assistant__name", "related_project__title")
    ordering = ("-timestamp",)

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    tag_list.short_description = "Tags"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "embedding_id")
    search_fields = ("name",)
    ordering = ("name",)

    def embedding_id(self, obj):
        return str(obj.embedding_id)[:8] if obj.embedding_id else "—"

    embedding_id.short_description = "Embedding ID"


@admin.register(AssistantProject)
class AssistantProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "assistant", "created_at")
    search_fields = ("title", "assistant__name")


@admin.register(AssistantObjective)
class AssistantObjectiveAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "is_completed", "created_at")
    search_fields = ("title", "project__title")
    list_filter = ("is_completed", "created_at")
    ordering = ("-created_at",)


@admin.register(AssistantNextAction)
class AssistantNextActionAdmin(admin.ModelAdmin):
    list_display = ("content", "objective", "completed", "created_at")
    list_filter = ("completed",)
    search_fields = ("content", "objective__title")
    ordering = ("-created_at",)


@admin.register(AssistantMemoryChain)
class AssistantMemoryChainAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "mode", "created_at")
    list_filter = ("mode", "project")
    search_fields = ("title", "project__title")
    filter_horizontal = ("filter_tags",)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "assistant", "user", "created_at")
    list_filter = ("assistant", "narrative_thread")
    search_fields = ("session_id", "assistant__name", "user__username")


@admin.register(AssistantReflectionLog)
class AssistantReflectionLogAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "mood", "created_at")
    search_fields = ("title", "summary", "project__title")
    list_filter = ("mood", "created_at")
    ordering = ("-created_at",)


@admin.register(DelegationEvent)
class DelegationEventAdmin(admin.ModelAdmin):
    list_display = (
        "parent_assistant",
        "child_assistant",
        "created_at",
    )
    list_filter = ("created_at",)


@admin.register(SessionHandoff)
class SessionHandoffAdmin(admin.ModelAdmin):
    list_display = ("from_assistant", "to_assistant", "session", "created_at")
    list_filter = ("created_at",)


@admin.register(SpecializationDriftLog)
class SpecializationDriftLogAdmin(admin.ModelAdmin):
    list_display = ("assistant", "drift_score", "trigger_type", "timestamp")
    list_filter = ("trigger_type", "auto_flagged", "resolved")
    search_fields = ("assistant__name", "summary")


@admin.register(DelegationStrategy)
class DelegationStrategyAdmin(admin.ModelAdmin):
    list_display = (
        "assistant",
        "prefer_specialists",
        "trust_threshold",
        "max_active_delegations",
    )


# @admin.register(AssistantMemoryChain)
# class AssistantMemoryChainAdmin(admin.ModelAdmin):
#     list_display = ("title", "project", "mode", "created_at")
#     list_filter = ("mode", "created_at")
#     filter_horizontal = ("memories", "filter_tags")
