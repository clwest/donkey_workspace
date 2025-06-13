from __future__ import annotations

from typing import Dict, Any

from embeddings.models import Embedding


def infer_embedding_metadata(embedding: Embedding) -> Dict[str, Any]:
    """Infer session_id and source_type metadata for an embedding."""
    obj = embedding.content_object
    if obj is None:
        return {}

    session_id = None
    source_type = None

    # DocumentChunk -> Document
    from intel_core.models import Document, DocumentChunk
    from memory.models import MemoryEntry
    from prompts.models import Prompt

    if isinstance(obj, DocumentChunk):
        document = obj.document
        session_id = getattr(document, "session_id", None)
        source_type = getattr(document, "source_type", None)
    elif isinstance(obj, Document):
        session_id = getattr(obj, "session_id", None)
        source_type = getattr(obj, "source_type", None)
    elif isinstance(obj, MemoryEntry):
        session_id = getattr(obj, "session_id", None)
        source_type = obj.type or "memory"
    elif isinstance(obj, Prompt):
        # Use linked document if available
        if obj.source_document:
            session_id = getattr(obj.source_document, "session_id", None)
            source_type = getattr(obj.source_document, "source_type", None)
        else:
            source_type = "prompt"
    else:
        # Generic fallback: use attributes if present
        session_id = getattr(obj, "session_id", None)
        source_type = getattr(obj, "source_type", None)

    result: Dict[str, Any] = {}
    if embedding.session_id is None and session_id:
        result["session_id"] = session_id
    if embedding.source_type is None and source_type:
        result["source_type"] = source_type
    return result
