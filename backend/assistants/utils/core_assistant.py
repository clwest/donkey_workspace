import logging
from typing import Optional

from assistants.models import Assistant, AssistantThoughtLog, AssistantReflectionLog
from intel_core.models import Document
from project.models import Project
from memory.models import MemoryEntry

from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine

logger = logging.getLogger(__name__)


class CoreAssistant:
    def __init__(self, assistant: Assistant):
        self.assistant = assistant
        self.thought_engine = AssistantThoughtEngine(assistant)
        self.reflection_engine = AssistantReflectionEngine(assistant)

    def think(self, user_input: str) -> Optional[AssistantThoughtLog]:
        """
        Trigger a reasoning trace from the assistant using the ThoughtEngine.
        """
        logger.info(f"[CoreAssistant] Thinking on: {user_input}")
        return self.thought_engine.generate_thought(user_input)

    def reflect_now(self) -> Optional[AssistantReflectionLog]:
        """
        Run a general reflection based on recent thoughts and memory.
        """
        logger.info(f"[CoreAssistant] Reflecting on recent activity...")
        return self.reflection_engine.reflect_on_recent_activity()

    def reflect_on_doc(self, doc: Document) -> Optional[AssistantReflectionLog]:
        """
        Reflect on a specific document and log a Reflection.
        """
        logger.info(f"[CoreAssistant] Reflecting on document: {doc.slug}")
        return self.reflection_engine.reflect_on_document(doc)

    def log_thought(self, content: str, tags: list[str] = []) -> AssistantThoughtLog:
        """
        Manually log a thought for the assistant.
        """
        logger.info(f"[CoreAssistant] Logging manual thought: {content[:50]}...")
        return AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            content=content,
            tags=tags,
        )

    def save_to_memory(self, content: str, project: Optional[Project] = None, label: Optional[str] = None) -> MemoryEntry:
        """
        Save a string to assistant memory with optional project linkage.
        """
        logger.info(f"[CoreAssistant] Saving to memory: {label or content[:30]}...")
        return MemoryEntry.objects.create(
            event=content,
            source_user=None,
            related_project=project,
            label=label or "Auto Memory Save",
        )

    def suggest_next_action(self, context: str) -> str:
        """
        Placeholder for LLM-driven planning.
        """
        logger.info(f"[CoreAssistant] Suggesting next action for: {context[:50]}")
        return "(TODO: Suggest next action based on context.)"
