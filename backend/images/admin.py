from django.contrib import admin
from .models import (
    Image,
    SourceImage,
    UpscaleImage,
    Edit,
    PromptHelper,
    PromptHelperVersion,
    PromptPlacement,
    TagImage,
    ProjectImage,
    StableDiffusionUsageLog,
    ThemeHelper,
)
from django.utils.html import mark_safe


@admin.register(PromptPlacement)
class PromptPlacementAdmin(admin.ModelAdmin):
    list_display = ("name", "prompt_type", "placement", "is_enabled", "created_at")
    list_filter = ("prompt_type", "placement", "is_enabled")
    search_fields = ("name", "description")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "prompt_preview",
        "model_backend",
        "status",
        "created_at",
        "has_output_url",
        "story_id",
        "is_favorite",
    )
    search_fields = ("prompt", "negative_prompt", "description")
    list_filter = (
        "status",
        "model_backend",
        "is_favorite",
        "engine_used",
        "model_used",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Prompt")
    def prompt_preview(self, obj):
        return (obj.prompt[:50] + "...") if obj.prompt else "—"

    @admin.display(description="🌐 Image?")
    def has_output_url(self, obj):
        return bool(obj.output_url)

    @admin.display(description="📖 Story")
    def story_id(self, obj):
        return obj.story.id if obj.story else "—"


@admin.register(SourceImage)
class SourceImageAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "purpose", "is_public", "uploaded_at")
    list_filter = ("purpose", "is_public")
    search_fields = ("title", "description")
    ordering = ("-uploaded_at",)


@admin.register(UpscaleImage)
class UpscaleImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "aspect_ratio",
        "upscale_type",
        "created_at",
        "output_url",
    )
    search_fields = ("upscale_type",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Edit)
class EditAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "edit_type", "created_at", "output_url")
    search_fields = ("prompt", "edit_type")
    list_filter = ("edit_type",)
    readonly_fields = ("created_at",)


## Inline for PromptHelper versions
class PromptHelperVersionInline(admin.TabularInline):
    model = PromptHelperVersion
    extra = 1
    fields = ("version_number", "prompt", "negative_prompt", "notes", "created_at")
    readonly_fields = ("version_number", "created_at")
    can_delete = False


@admin.register(PromptHelper)
class PromptHelperAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "is_builtin", "is_fork", "created_by")
    list_filter = ("is_builtin", "is_fork", "category")
    search_fields = ("name", "prompt", "tags")
    ordering = ("-created_at",)
    filter_horizontal = ("placements",)  # Enables multi-select in admin
    # Inline versions for prompt helpers
    inlines = [PromptHelperVersionInline]


@admin.register(TagImage)
class TagImageAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "is_published", "is_featured", "created_at")
    search_fields = ("name", "description")
    list_filter = ("is_published", "is_featured")
    ordering = ("-created_at",)


@admin.register(StableDiffusionUsageLog)
class StableDiffusionUsageLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "estimated_credits_used", "created_at", "image_id")
    search_fields = ("prompt",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    @admin.display(description="Image ID")
    def image_id(self, obj):
        return obj.image.id if obj.image else "—"


# Admin for PromptHelperVersion
@admin.register(PromptHelperVersion)
class PromptHelperVersionAdmin(admin.ModelAdmin):
    list_display = ("helper", "version_number", "created_at")
    readonly_fields = ("version_number", "created_at")
    actions = ["rollback_to_version"]

    def rollback_to_version(self, request, queryset):
        for ver in queryset:
            helper = ver.helper
            helper.current_version = ver
            helper.prompt = ver.prompt
            helper.negative_prompt = ver.negative_prompt
            helper.save(update_fields=["current_version", "prompt", "negative_prompt"])
        self.message_user(
            request, f"Rolled back to version(s) for {queryset.count()} selection(s)"
        )

    rollback_to_version.short_description = "Rollback selected version(s) to current"


@admin.register(ThemeHelper)
class ThemeHelperAdmin(admin.ModelAdmin):
    # Show preview thumbnail, name, category, prompt
    list_display = [
        "preview_thumb",
        "name",
        "category",
        "is_public",
        "is_featured",
        "created_by",
        "prompt",
    ]
    list_filter = ["category", "is_public", "is_featured", "created_by"]
    search_fields = ["name", "description", "tags"]
    autocomplete_fields = ["recommended_styles", "parent"]
    readonly_fields = ["preview_thumb"]

    def preview_thumb(self, obj):
        if obj.preview_image and hasattr(obj.preview_image, "url"):
            return mark_safe(
                f'<img src="{obj.preview_image.url}" width="60" height="60" style="object-fit: cover; border-radius: 4px;"/>'
            )
        return ""

    preview_thumb.short_description = "Preview"
