"""Deprecated loader referencing new document service."""

from core.services.document_service import ingest_pdfs as load_pdfs

__all__ = ["load_pdfs"]
