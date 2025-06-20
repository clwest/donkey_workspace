from django.contrib import admin
from .models import (
    Document,
    DocumentInteraction,
    JobStatus,
    DocumentProgress,
    DocumentUploadLog,
    GlossaryMissReflectionLog,
    GlossaryFallbackReflectionLog,
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "upload_status", "created_at")
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
        "warning_badge",
        "status_color",
        "processed",
        "embedded_chunks",
        "total_chunks",
    )
    readonly_fields = ("progress_id", "created_at", "updated_at")
    list_filter = ("status", "created_at")

    def status_color(self, obj):
        from django.utils.html import format_html

        color = {
            "failed": "red",
            "pending": "gray",
            "in_progress": "orange",
            "completed": "green",
        }.get(obj.status, "black")
        return format_html("<span style='color:{};'>{}</span>", color, obj.status)

    status_color.short_description = "Status"

    @admin.display(description="")
    def warning_badge(self, obj):
        from django.utils.html import format_html
        doc = Document.objects.filter(metadata__progress_id=str(obj.progress_id)).first()
        if not doc:
            return ""
        total = doc.chunks.count()
        embedded = doc.chunks.filter(embedding_status="embedded").count()
        missing = doc.chunks.filter(embedding_status="embedded", embedding__isnull=True).exists()
        if missing or obj.total_chunks != total or obj.embedded_chunks != embedded:
            return format_html("<span style='color:orange;'>⚠️</span>")
        return ""



@admin.register(GlossaryMissReflectionLog)
class GlossaryMissReflectionLogAdmin(admin.ModelAdmin):
    list_display = ("anchor", "user_question", "created_at")
    search_fields = ("user_question", "assistant_response")


@admin.register(GlossaryFallbackReflectionLog)
class GlossaryFallbackReflectionLogAdmin(admin.ModelAdmin):
    list_display = ("anchor_slug", "chunk_id", "created_at")
    search_fields = ("assistant_response",)


@admin.register(DocumentUploadLog)
class DocumentUploadLogAdmin(admin.ModelAdmin):
    list_display = ("document", "action", "user", "created_at")
    list_filter = ("action", "created_at")
