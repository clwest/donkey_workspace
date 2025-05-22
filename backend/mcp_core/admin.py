# Register your models here.
from django.contrib import admin
from .models import MemoryContext, DevDoc, PublicEventLog


# from mcp_core.utils.agent_reflection import AgentReflectionEngine


@admin.register(MemoryContext)
class MemoryContextAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "target_type",
        "target_id",
        "content",
        "important",
        "created_at",
    )
    list_filter = ["important", "created_at"]
    search_fields = ("content", "target_id")
    ordering = ("-created_at",)


@admin.register(DevDoc)
class DevDocAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at")
    search_fields = ("title", "content")


@admin.register(PublicEventLog)
class PublicEventLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor_name", "success")
    list_filter = ("success",)
    search_fields = ("actor_name", "event_details")
    ordering = ("-timestamp",)
