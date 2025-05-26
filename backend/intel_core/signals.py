"""Deprecated signal hooks for search vector updates."""

# These functions previously managed a ``search_vector`` field on
# ``Document`` instances via ``pre_save`` and ``post_save`` signals.
# The ``Document`` model no longer includes that field, so the signal
# handlers have been removed.  This module remains to avoid import
# errors from any legacy code.


def update_document_search_vector(sender, instance, **kwargs):
    """Deprecated stub kept for backward compatibility."""
    pass

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from memory.models import MemoryEntry
from .models import DocumentChunk


@receiver(post_save, sender=DocumentChunk)
def create_memory_from_chunk(sender, instance, created, **kwargs):
    if created:
        MemoryEntry.objects.create(
            event=instance.text[:200],
            summary=instance.text[:200],
            document=instance.document,
            linked_content_type=ContentType.objects.get_for_model(DocumentChunk),
            linked_object_id=instance.id,
            type="document_chunk",
        )

