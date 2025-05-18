from django.contrib import admin
from .models import Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "theme",
        "prompt",
        "created_at",
        "updated_at",
        "has_text",
        "has_image",
        "has_audio",
    )
    list_filter = ("created_at", "updated_at", "theme", "status")
    search_fields = ("prompt", "generated_text", "theme", "tags")
    ordering = ("-created_at",)

    @admin.display(description="📝 Text")
    def has_text(self, obj):
        return bool(obj.generated_text)

    @admin.display(description="🖼️ Image")
    def has_image(self, obj):
        return bool(obj.image and getattr(obj.image, "image", None))

    @admin.display(description="🔊 Audio")
    def has_audio(self, obj):
        return bool(obj.tts and getattr(obj.tts, "audio_file", None))
