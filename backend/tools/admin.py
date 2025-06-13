from django.contrib import admin

from .models import Tool, ToolUsageLog, ToolDiscoveryLog, ToolExecutionLog


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "enabled", "is_public", "is_active")
    search_fields = ("name", "slug")
    list_filter = ("enabled", "is_public", "is_active")

    actions = ["enable_tools", "disable_tools", "test_tools"]

    def enable_tools(self, request, queryset):
        queryset.update(enabled=True)

    def disable_tools(self, request, queryset):
        queryset.update(enabled=False)

    def test_tools(self, request, queryset):
        from .utils.tool_registry import execute_tool

        for tool in queryset:
            try:
                execute_tool(tool, {})
                self.message_user(request, f"{tool.slug} executed")
            except Exception as exc:  # pragma: no cover - admin util
                self.message_user(request, f"{tool.slug} failed: {exc}", level="error")


@admin.register(ToolDiscoveryLog)
class ToolDiscoveryLogAdmin(admin.ModelAdmin):
    list_display = ("tool", "path", "success", "created_at")
    list_filter = ("success", "created_at")


@admin.register(ToolExecutionLog)
class ToolExecutionLogAdmin(admin.ModelAdmin):
    list_display = ("tool", "success", "status_code", "created_at")
    list_filter = ("success", "status_code")
    search_fields = ("tool__name", "tool__slug")
    autocomplete_fields = ("tool", "assistant", "agent")


# @admin.register(ToolUsageLog)
# class ToolUsageLogAdmin(admin.ModelAdmin):
#     list_display = ("tool", "status", "created_at")
#     list_filter = ("status", "created_at")
#     # search_fields = ("tool__name", "tool__slug")
#     autocomplete_fields = ("tool", "assistant", "agent")
