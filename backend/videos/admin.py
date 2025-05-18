from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "model_backend",
        "provider",
        "prediction_id",
        "created_at",
    )
    list_filter = ("status", "model_backend", "provider")
    search_fields = ("prompt", "error_message", "prediction_id")
