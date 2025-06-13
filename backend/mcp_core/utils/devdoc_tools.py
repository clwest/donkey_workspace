from typing import Optional
from django.utils.text import slugify
from mcp_core.models import DevDoc
from intel_core.models import Document


def link_document_to_devdoc(devdoc: DevDoc, document: Document) -> None:
    """Ensure devdoc.linked_document is set to the given document."""
    if devdoc.linked_document_id != document.id:
        devdoc.linked_document = document
        devdoc.save(update_fields=["linked_document"])


def create_summary_from_doc(document: Document, max_len: int = 400) -> str:
    """Generate a basic summary if document.summary is missing."""
    if document.summary:
        return document.summary

    text = document.content or ""
    summary = text.strip().split("\n")[0][:max_len]
    document.summary = summary
    document.save(update_fields=["summary"])
    return summary
