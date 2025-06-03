from django.contrib import admin
from .models import Embedding

# Register your models here.


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = (

        "content_type",
        "content_id",
        "short_embedding",
        "created_at",
    )
    list_filter = ("content_type",)
    search_fields = ("content_id",)

    @admin.display(description="Embedding Preview")
    def short_embedding(self, obj) -> str:
        """Return a short, human friendly preview of the vector."""
        vector = obj.embedding
        if vector is None:
            return "—"

        # pgvector may return a list or numpy array. Avoid boolean evaluation
        try:
            vector_list = (
                vector.tolist() if hasattr(vector, "tolist") else list(vector)
            )
        except Exception:
            # Fallback to string representation on unexpected types
            return str(vector)[:20] + "..."

        snippet = ", ".join(f"{x:.4f}" for x in vector_list[:3])
        return f"[{snippet}...]"

