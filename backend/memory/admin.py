from django.contrib import admin
from .models import SymbolicMemoryAnchor


@admin.register(SymbolicMemoryAnchor)
class SymbolicMemoryAnchorAdmin(admin.ModelAdmin):
    list_display = ("slug", "label", "created_at")

