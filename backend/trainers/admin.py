from django.contrib import admin
from .models import ReplicateModel, ReplicatePrediction


@admin.register(ReplicateModel)
class ReplicateModelAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "version")


@admin.register(ReplicatePrediction)
class ReplicatePredictionAdmin(admin.ModelAdmin):
    list_display = ("status", "prompt", "model", "created_at", "completed_at")
    list_filter = ("status", "model")
    search_fields = ("prompt", "prediction_id")
