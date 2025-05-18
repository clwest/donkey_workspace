from django.contrib import admin
from .models import StoryAudio


@admin.register(StoryAudio)
class StoryAudioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "voice_style",
        "provider",
        "model_backend",
        "status",
        "has_audio",
        "created_at",
    )
    search_fields = ("prompt", "voice_style", "theme")
    list_filter = ("status", "provider", "model_backend", "voice_style")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    @admin.display(description="🔊 Audio File?")
    def has_audio(self, obj):
        return bool(obj.audio_file)
