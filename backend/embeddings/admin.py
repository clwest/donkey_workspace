from django.contrib import admin
from .models import Embedding, EmbeddingDebugTag
from intel_core.models import DocumentChunk as Chunk

# Register your models here.


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = (
        "content_type",
        "content_id",
        "content_preview",
        "short_embedding",
        "created_at",
    )
    list_filter = ("content_type",)
    search_fields = ("content_id",)

    @admin.display(description="Content")
    def content_preview(self, obj) -> str:
        """Return first 50 characters of chunk text or stored content."""
        text = obj.content
        if not text and obj.content_type and obj.content_type.model == "documentchunk":
            chunk = Chunk.objects.filter(id=obj.object_id).first()
            if chunk:
                text = chunk.text
        if not text:
            return "—"
        return text[:50] + ("..." if len(text) > 50 else "")

    @admin.display(description="Embedding Preview")
    def short_embedding(self, obj) -> str:
        """Return a short, human friendly preview of the vector."""
        vector = obj.embedding
        if vector is None:
            return "—"

        # pgvector may return a list or numpy array. Avoid boolean evaluation
        try:
            vector_list = vector.tolist() if hasattr(vector, "tolist") else list(vector)
        except Exception:
            # Fallback to string representation on unexpected types
            return str(vector)[:20] + "..."

        snippet = ", ".join(f"{x:.4f}" for x in vector_list[:3])
        return f"[{snippet}...]"


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "order",
        "score",
        "glossary_boost",
        "force_embed",
        "is_drifting",
        "status_colored",
        "last_used_in_chat",
    )
    list_filter = ("embedding_status", "force_embed")
    search_fields = ("document__title", "document__id", "id")

    @admin.display(description="Status")
    def status_colored(self, obj):
        from django.utils.html import format_html

        color = (
            "red"
            if obj.embedding_status in {"pending", "skipped"} and obj.score > 0.3
            else "black"
        )
        return format_html(
            "<span style='color:{};'>{}</span>", color, obj.embedding_status
        )

    @admin.display(boolean=True)
    def last_used_in_chat(self, obj):
        from assistants.models.thoughts import AssistantThoughtLog

        return AssistantThoughtLog.objects.filter(
            fallback_details__chunk_ids__contains=[str(obj.id)]
        ).exists()


@admin.register(EmbeddingDebugTag)
class EmbeddingDebugTagAdmin(admin.ModelAdmin):
    list_display = ("embedding_id", "reason", "status", "repaired_at", "created_at")
    search_fields = ("embedding_id", "reason", "notes")
