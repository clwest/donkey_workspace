from django.contrib import admin

from .models import (
    CustomUser,
    UserMemory,
    UserPrompts,
    UserInteractionSummary,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff")


@admin.register(UserMemory)
class UserMemoryAdmin(admin.ModelAdmin):
    list_display = ("user", "memory_key", "created_at")


@admin.register(UserPrompts)
class UserPromptsAdmin(admin.ModelAdmin):
    list_display = ("user", "prompt_key", "created_at")


@admin.register(UserInteractionSummary)
class UserInteractionSummaryAdmin(admin.ModelAdmin):
    list_display = ("user", "period_start", "period_end")
