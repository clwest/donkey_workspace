from django.contrib import admin

from .models.assistant import Assistant
from .models.thoughts import AssistantThoughtLog
from .models.project import (
    AssistantProject,
    AssistantObjective,
    AssistantNextAction,
)
from .models.reflection import AssistantReflectionLog
from .models.assistant import (
    ChatSession,
    StructuredMemory,
    TokenUsage,
    AssistantChatMessage,
    AudioResponse,
    DelegationEvent,
    DelegationStrategy,
    AssistantMessage,
    RoutingSuggestionLog,
    SessionHandoff,
    AssistantSwitchEvent,
    AssistantHandoffLog,
    SpecializationDriftLog,
    ChatIntentDriftLog,
    DebateSession,
    DebateThoughtLog,
    DebateSummary,
)
from .models.glossary import SuggestionLog
from .models.core import AssistantMythLayer
from .models.thoughts import CollaborationLog, CollaborationThread
from .models.project import AssistantMemoryChain
from .models.diagnostics import AssistantDiagnosticReport
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
        "is_featured",
        "featured_rank",
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
                    "intro_text",
                    "archetype_summary",
                    "preferred_model",
                    "memory_mode",
                    "thinking_style",
                )
            },
        ),
        (
            "Meta",
            {
                "fields": (
                    "is_active",
                    "is_demo",
                    "is_featured",
                    "featured_rank",
                    "show_intro_splash",
                    "auto_start_chat",
                    "created_by",
                    "created_at",
                )
            },
        ),
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


@admin.register(AssistantHandoffLog)
class AssistantHandoffLogAdmin(admin.ModelAdmin):
    list_display = ("from_assistant", "to_assistant", "project", "created_at")
    list_filter = ("created_at",)


@admin.register(SpecializationDriftLog)
class SpecializationDriftLogAdmin(admin.ModelAdmin):
    list_display = ("assistant", "drift_score", "trigger_type", "timestamp")
    list_filter = ("trigger_type", "auto_flagged", "resolved")
    search_fields = ("assistant__name", "summary")


@admin.register(ChatIntentDriftLog)
class ChatIntentDriftLogAdmin(admin.ModelAdmin):
    list_display = ("assistant", "drift_score", "created_at")
    list_filter = ("assistant",)


@admin.register(SuggestionLog)
class SuggestionLogAdmin(admin.ModelAdmin):
    list_display = (
        "assistant",
        "anchor_slug",
        "suggested_action",
        "score",
        "status",
        "created_at",
    )
    list_filter = ("status", "assistant")


@admin.register(DelegationStrategy)
class DelegationStrategyAdmin(admin.ModelAdmin):
    list_display = (
        "assistant",
        "prefer_specialists",
        "trust_threshold",
        "max_active_delegations",
    )


@admin.register(CollaborationLog)
class CollaborationLogAdmin(admin.ModelAdmin):
    list_display = ("project", "style_conflict_detected", "created_at")
    filter_horizontal = ("participants",)


@admin.register(CollaborationThread)
class CollaborationThreadAdmin(admin.ModelAdmin):
    list_display = ("lead", "created_at")
    filter_horizontal = ("participants",)


@admin.register(AssistantMythLayer)
class AssistantMythLayerAdmin(admin.ModelAdmin):
    list_display = ("assistant", "last_updated")


@admin.register(AssistantDiagnosticReport)
class AssistantDiagnosticReportAdmin(admin.ModelAdmin):
    list_display = (
        "assistant",
        "generated_at",
        "fallback_rate",
        "glossary_success_rate",
        "avg_chunk_score",
        "rag_logs_count",
    )


# @admin.register(AssistantMemoryChain)
# class AssistantMemoryChainAdmin(admin.ModelAdmin):
#     list_display = ("title", "project", "mode", "created_at")
#     list_filter = ("mode", "created_at")
#     filter_horizontal = ("memories", "filter_tags")
