from django.contrib import admin
from .models import Document, DocumentInteraction, JobStatus, DocumentProgress


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "created_at")
    search_fields = ("title", "content", "url")
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
    list_display = ("progress_id", "title", "status", "processed", "total_chunks")
    readonly_fields = ("progress_id", "created_at", "updated_at")
    list_filter = ("status", "created_at")
