"""Deprecated loader referencing new document service."""

from core.services.document_service import ingest_urls as load_urls

__all__ = ["load_urls"]
