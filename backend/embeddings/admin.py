from django.contrib import admin
from .models import Embedding

# Register your models here.


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = (
        "id",  # Optional UUID
        "content_type",
        "object_id",
        "short_content",
        "short_embedding",
        "session_id",
        "created_at",
    )
    list_filter = ("content_type", "created_at")
    search_fields = ("content", "object_id", "session_id")

    def short_content(self, obj):
        return (obj.content[:75] + "...") if obj.content else "—"

    def short_embedding(self, obj):
        return (
            f"[{', '.join(f'{x:.4f}' for x in obj.embedding[:3])}...]" if obj.embedding else "—"
        )

    short_content.short_description = "Content Preview"
    short_embedding.short_description = "Embedding (preview)"
