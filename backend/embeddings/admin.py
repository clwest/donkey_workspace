from django.contrib import admin
from .models import Embedding

# Register your models here.


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ("content_type", "content_id", "created_at")
    list_filter = ("content_type",)
    search_fields = ("content_id",)
