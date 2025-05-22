from assistants.models.assistant import Assistant
from assistants.models.thoughts import AssistantThoughtLog
from prompts.models import Prompt


def create_prompt_revision(assistant: Assistant, mutation_mode: str = "clarify") -> Prompt | None:
    """Clone and slightly mutate the assistant's system prompt."""
    original = assistant.system_prompt
    if not original:
        return None
    new_content = f"{original.content}\n\n[Revised: {mutation_mode}]"
    new_prompt = Prompt.objects.create(
        title=f"{original.title} (rev)",
        type=original.type,
        content=new_content,
        source=f"recovery:{assistant.slug}",
        parent=original,
    )
    assistant.system_prompt = new_prompt
    assistant.save(update_fields=["system_prompt"])
    AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought="System prompt revised during recovery.",
        thought_type="mutation",
        category="insight",
    )
    return new_prompt


def generate_recovery_summary(assistant: Assistant) -> str:
    logs = assistant.drift_logs.order_by("-timestamp")[:3]
    parts = [f"Drift {l.drift_score:.2f} on {l.timestamp.date()}" for l in logs]
    memory_count = assistant.thoughts.count()
    parts.append(f"Total thoughts: {memory_count}")
    return "; ".join(parts)
