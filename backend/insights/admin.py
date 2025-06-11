from django.contrib import admin
from .models import SymbolicAgentInsightLog


@admin.register(SymbolicAgentInsightLog)
class SymbolicAgentInsightLogAdmin(admin.ModelAdmin):
    list_display = (
        "agent",
        "document",
        "symbol",
        "conflict_score",
        "resolution_method",
        "created_at",
    )
    search_fields = ("symbol", "notes")
