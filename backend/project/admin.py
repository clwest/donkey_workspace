from django.contrib import admin
from .models import Project, ProjectTask, ProjectMilestone, ProjectMemoryLink


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "user", "project_type", "status", "created_at")
    search_fields = ("title", "slug", "user__username")
    list_filter = ("project_type", "status", "created_at", "narrative_thread")
    ordering = ("-created_at",)
    readonly_fields = ("slug", "created_at", "updated_at")


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "created_at")
    list_filter = ("status", "priority", "created_at")
    search_fields = ("title", "notes", "project__title")


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "due_date", "is_completed")
    list_filter = ("status", "due_date")
    search_fields = ("title", "description", "project__title")


@admin.register(ProjectMemoryLink)
class ProjectMemoryLinkAdmin(admin.ModelAdmin):
    list_display = ("project", "memory", "linked_at")
    search_fields = ("project__title", "memory__content")
    ordering = ("-linked_at",)
