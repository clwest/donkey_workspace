from django.contrib import admin
from .models import CharacterProfile, CharacterStyle, CharacterReferenceImage
from .models import CharacterTrainingProfile


@admin.register(CharacterProfile)
class CharacterProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "is_public", "created_by", "created_at")
    search_fields = ("name", "description")
    list_filter = ("is_public", "created_at")
    ordering = ("-created_by",)


@admin.register(CharacterStyle)
class CharacterStyleAdmin(admin.ModelAdmin):
    # Link to PromptHelper and show synced prompts
    raw_id_fields = ("prompt_helper",)
    list_display = (
        "id",
        "style_name",
        "prompt_helper",
        "prompt",
        "negative_prompt",
        "character",
        "created_at",
    )
    search_fields = ("style_name", "prompt", "prompt_helper__name")
    list_filter = ("prompt_helper",)
    ordering = ("-created_at",)


@admin.register(CharacterReferenceImage)
class CharacterReferenceImageAdmin(admin.ModelAdmin):
    list_display = ("id", "character", "image", "created_at")
    search_fields = ("character__name",)
    ordering = ("-created_at",)


@admin.register(CharacterTrainingProfile)
class CharacterTrainingProfileAdmin(admin.ModelAdmin):
    list_display = ("character", "status", "created_at", "updated_at")
    search_fields = ("character__name", "status")
    ordering = ("-updated_at",)
