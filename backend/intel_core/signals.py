"""Deprecated signal hooks for search vector updates."""

# These functions previously managed a ``search_vector`` field on
# ``Document`` instances via ``pre_save`` and ``post_save`` signals.
# The ``Document`` model no longer includes that field, so the signal
# handlers have been removed.  This module remains to avoid import
# errors from any legacy code.


def update_document_search_vector(sender, instance, **kwargs):
    """Deprecated stub kept for backward compatibility."""
    pass
