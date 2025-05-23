from django.contrib import admin
from .models import (
    CinemythStoryline,
    MythcastingChannel,
    AudienceFeedbackLoop,
    ParticipatoryStreamEvent,
)


@admin.register(CinemythStoryline)
class CinemythStorylineAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)


@admin.register(MythcastingChannel)
class MythcastingChannelAdmin(admin.ModelAdmin):
    list_display = ("channel_name", "active_storyline", "created_at")
    search_fields = ("channel_name",)


@admin.register(AudienceFeedbackLoop)
class AudienceFeedbackLoopAdmin(admin.ModelAdmin):
    list_display = ("channel", "symbolic_trigger", "codex_alignment_shift", "created_at")
    search_fields = ("symbolic_trigger",)


@admin.register(ParticipatoryStreamEvent)
class ParticipatoryStreamEventAdmin(admin.ModelAdmin):
    list_display = ("initiating_viewer_id", "linked_channel", "codex_modified", "created_at")
    search_fields = ("initiating_viewer_id",)
