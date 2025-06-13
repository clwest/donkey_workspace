from django.contrib import admin

from .models import Agent, AgentThought, SwarmJournalEntry


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    """Admin configuration for :class:`Agent`."""

    search_fields = ("name", "slug", "specialty")
    list_display = (
        "name",
        "slug",
        "agent_type",
        "preferred_llm",
        "execution_mode",
        "is_active",
    )
    list_filter = ("agent_type", "preferred_llm", "execution_mode", "is_active")


@admin.register(AgentThought)
class AgentThoughtAdmin(admin.ModelAdmin):
    search_fields = ("agent__name", "agent__slug")
    list_display = ("agent", "created_at")


@admin.register(SwarmJournalEntry)
class SwarmJournalEntryAdmin(admin.ModelAdmin):
    search_fields = ("content",)

