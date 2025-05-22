"""Core service layer consolidating cross-app logic."""

from .assistant_service import create_assistant, spawn_delegated_assistant
from .memory_service import reflect_on_memory
from .agent_service import spawn_agent_for_skill
from .document_service import ingest_documents

__all__ = [
    "create_assistant",
    "spawn_delegated_assistant",
    "reflect_on_memory",
    "spawn_agent_for_skill",
    "ingest_documents",
]
