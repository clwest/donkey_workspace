"""Deprecated loader referencing new document service."""

from core.services.document_service import ingest_videos as load_videos

__all__ = ["load_videos"]
