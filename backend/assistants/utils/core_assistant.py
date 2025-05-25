import logging
from typing import Optional

from assistants.models.assistant import Assistant
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.project import AssistantProject
from assistants.utils.delegation import spawn_delegated_assistant
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

    def save_to_memory(
        self,
        content: str,
        project: Optional[Project] = None,
        label: Optional[str] = None,
    ) -> MemoryEntry:
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

    def reflect_on_assistant(
        self, assistant: Assistant, project: AssistantProject
    ) -> Optional[str]:
        """Run reflection about a delegated assistant."""
        logger.info(f"[CoreAssistant] Reflecting on assistant {assistant.slug}")
        return self.reflection_engine.reflect_on_assistant(assistant, project)

    def delegate_from_memory(
        self,
        memory_entry: Optional[MemoryEntry] = None,
        *,
        reason: str = "delegation",
        summary: Optional[str] = None,
    ) -> Assistant:
        """Spawn a delegated assistant using memory context."""
        logger.info("[CoreAssistant] Spawning delegated assistant from memory")
        return spawn_delegated_assistant(
            parent_or_session=self.assistant,
            project=None,
            name=None,
            description="",
            specialty="",
            narrative_thread=None,
            memory_entry=memory_entry,
            reason=reason,
            summary=summary,
        )

    def run_task(self, task: str) -> dict:
        """Execute a simple natural language task."""
        logger.info(f"[CoreAssistant] Running task: {task}")
        prompt = f"You are {self.assistant.name}. Complete this task:\n{task}"
        try:
            result_text = self.thought_engine.generate_thought(prompt)
            log_info = self.thought_engine.log_thought(
                result_text, thought_type="task"
            )
            return {
                "result": result_text,
                "log_id": str(log_info.get("log").id) if log_info.get("log") else None,
            }
        except Exception as e:  # pragma: no cover - safeguard
            logger.error("[CoreAssistant] run_task failed: %s", e)
            return {"result": "Task failed.", "error": str(e)}
