from django.shortcuts import get_object_or_404

from ..models import MemoryEntry
from .convergence import (
    calculate_convergence_stats,
    recalculate_anchor_convergence,
)
from .anchor_confidence import get_anchor_confidence
from .feedback_engine import (
    apply_feedback_suggestion,
    extract_anchor_slugs,
)


class MemoryService:
    """Utility service for memory entry access."""

    @staticmethod
    def get_entry(entry_id):
        return MemoryEntry.objects.filter(id=entry_id).first()

    @staticmethod
    def get_entry_or_404(entry_id):
        return get_object_or_404(MemoryEntry, id=entry_id)

    @staticmethod
    def create_entry(**kwargs):
        return MemoryEntry.objects.create(**kwargs)

    @staticmethod
    def filter_entries(**filters):
        return MemoryEntry.objects.filter(**filters)
