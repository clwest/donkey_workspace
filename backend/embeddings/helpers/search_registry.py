# embeddings/helpers/search_registry.py

from embeddings.vector_utils import compute_similarity
from assistants.models import AssistantThoughtLog, AssistantReflectionLog
from memory.models import MemoryEntry
from mcp_core.models import MemoryContext, Plan, Task, DevDoc
from prompts.models import Prompt

search_registry = {
    "prompt": {
        "label": "Prompt",
        "model": Prompt,
        "queryset": lambda: Prompt.objects.exclude(embedding__isnull=True),
        "embedding_field": "embedding",
        "text_field": "content",
        "id_field": "id",
    },
    "memory": {
        "label": "MCP MemoryContext",
        "model": MemoryContext,
        "queryset": lambda: MemoryContext.objects.exclude(content=""),
        "embedding_field": None,  # not yet vectorized
        "text_field": "content",
        "id_field": "id",
    },
    "thought": {
        "label": "Assistant ThoughtLog",
        "model": AssistantThoughtLog,
        "queryset": lambda: AssistantThoughtLog.objects.exclude(thought=""),
        "embedding_field": None,  # not yet vectorized
        "text_field": "thought",
        "id_field": "id",
    },
    "project_reflection": {
        "label": "Assistant Project Reflection",
        "model": AssistantReflectionLog,
        "queryset": lambda: AssistantReflectionLog.objects.exclude(summary=""),
        "embedding_field": None,
        "text_field": "summary",
        "id_field": "id",
    },
    "plan": {
        "label": "MCP Plan",
        "model": Plan,
        "queryset": lambda: Plan.objects.exclude(description=""),
        "embedding_field": None,
        "text_field": "description",
        "id_field": "id",
    },
    "task": {
        "label": "MCP Task",
        "model": Task,
        "queryset": lambda: Task.objects.exclude(description=""),
        "embedding_field": None,
        "text_field": "description",
        "id_field": "id",
    },
    "memory_log": {
        "label": "Personal MemoryEntry",
        "model": MemoryEntry,
        "queryset": lambda: MemoryEntry.objects.exclude(event=""),
        "embedding_field": None,
        "text_field": "event",
        "id_field": "id",
    },
    "memory_reflection": {
        "label": "AssistantReflectionLog",
        "model": AssistantReflectionLog,
        "queryset": lambda: AssistantReflectionLog.objects.exclude(summary=""),
        "embedding_field": None,
        "text_field": "summary",
        "id_field": "id",
    },
    "devdoc": {
        "label": "Dev Doc",
        "model": DevDoc,
        "queryset": lambda: DevDoc.objects.exclude(embedding__isnull=True),
        "embedding_field": "embedding",
    }

}


# Added assistantthoughtlog registry
from assistants.models import AssistantThoughtLog

search_registry["assistantthoughtlog"] = {
    "label": "Assistant Thought",
    "model": AssistantThoughtLog,
    "queryset": lambda: AssistantThoughtLog.objects.exclude(embedding__isnull=True),
    "embedding_field": "embedding",
}