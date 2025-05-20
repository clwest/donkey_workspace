from django.contrib import admin

from .models import Tool, ToolUsageLog, ToolDiscoveryLog


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_enabled", "is_active", "agent_only")
    search_fields = ("name", "slug")
    list_filter = ("is_enabled", "is_active", "agent_only")


@admin.register(ToolDiscoveryLog)
class ToolDiscoveryLogAdmin(admin.ModelAdmin):
    list_display = ("tool", "path", "success", "created_at")
    list_filter = ("success", "created_at")


# @admin.register(ToolUsageLog)
# class ToolUsageLogAdmin(admin.ModelAdmin):
#     list_display = ("tool", "status", "created_at")
#     list_filter = ("status", "created_at")
#     # search_fields = ("tool__name", "tool__slug")
#     autocomplete_fields = ("tool", "assistant", "agent")
