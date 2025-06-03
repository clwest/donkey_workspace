from django.contrib import admin
from .models import (
    Document,
    DocumentInteraction,
    JobStatus,
    DocumentProgress,
    GlossaryMissReflectionLog,
    GlossaryFallbackReflectionLog,
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "created_at")
    search_fields = ("title", "content", "source_url")
    list_filter = ("source", "created_at")


@admin.register(DocumentInteraction)
class DocumentInteractionAdmin(admin.ModelAdmin):
    list_display = ("document", "user", "interaction_type", "timestamp")
    search_fields = ("document__title", "user__username")
    list_filter = ("interaction_type", "timestamp")


@admin.register(JobStatus)
class JobStatusAdmin(admin.ModelAdmin):
    list_display = (
        "job_id",
        "session_id",
        "status",
        "stage",
        "progress",
        "created_at",
    )
    readonly_fields = ("job_id", "created_at", "updated_at")
    search_fields = ("job_id", "status")
    list_filter = ("status", "created_at")

    def has_add_permission(self, request):
        # Jobs should only be created by the system
        return False


@admin.register(DocumentProgress)
class DocumentProgressAdmin(admin.ModelAdmin):
    list_display = (
        "progress_id",
        "title",
        "status_color",
        "processed_display",
        "embedded_display",
    )
    readonly_fields = ("progress_id", "created_at", "updated_at")
    list_filter = ("status", "created_at")

    def status_color(self, obj):
        from django.utils.html import format_html

        color = {
            "failed": "red",
            "pending": "orange",
            "in_progress": "blue",
            "completed": "green",
        }.get(obj.status, "black")
        return format_html("<span style='color:{};'>{}</span>", color, obj.status)

    status_color.short_description = "Status"

    def processed_display(self, obj):
        return f"{obj.processed} / {obj.total_chunks}"

    processed_display.short_description = "Processed"

    def embedded_display(self, obj):
        return f"{obj.embedded_chunks} / {obj.total_chunks}"

    embedded_display.short_description = "Embedded"


@admin.register(GlossaryMissReflectionLog)
class GlossaryMissReflectionLogAdmin(admin.ModelAdmin):
    list_display = ("anchor", "user_question", "created_at")
    search_fields = ("user_question", "assistant_response")


@admin.register(GlossaryFallbackReflectionLog)
class GlossaryFallbackReflectionLogAdmin(admin.ModelAdmin):
    list_display = ("anchor_slug", "chunk_id", "created_at")
    search_fields = ("assistant_response",)
