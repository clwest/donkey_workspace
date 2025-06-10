from django.contrib import admin
from .models import FeedbackEntry


@admin.register(FeedbackEntry)
class FeedbackEntryAdmin(admin.ModelAdmin):
    list_display = ["assistant_slug", "category", "created_at"]
    list_filter = ["category", "assistant_slug"]
    search_fields = ["description", "assistant_slug"]
