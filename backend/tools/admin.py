from django.contrib import admin

from .models import Tool, ToolUsageLog


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_enabled", "agent_only")
    search_fields = ("name", "slug")
    list_filter = ("is_enabled", "agent_only")


# @admin.register(ToolUsageLog)
# class ToolUsageLogAdmin(admin.ModelAdmin):
#     list_display = ("tool", "status", "created_at")
#     list_filter = ("status", "created_at")
#     # search_fields = ("tool__name", "tool__slug")
#     autocomplete_fields = ("tool", "assistant", "agent")
