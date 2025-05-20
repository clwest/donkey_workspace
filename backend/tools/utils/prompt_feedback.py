from typing import Optional
from assistants.models import AssistantPromptLink, AssistantReflectionLog, Assistant
from prompts.models import Prompt, PromptMutationLog
from prompts.utils.mutation import mutate_prompt
from .models import ToolUsageLog


def mutate_prompt_based_on_tool_feedback(
    log: ToolUsageLog,
    feedback: str,
    assistant: Optional[Assistant],
    message: str | None = None,
) -> Optional[Prompt]:
    """Mutate the assistant's prompt when tool feedback is negative."""
    if feedback not in {"not_helpful", "irrelevant", "error"}:
        return None
    if not assistant or not assistant.system_prompt:
        return None

    original = assistant.system_prompt
    mutated_text = mutate_prompt(original.content, "clarify")
    new_prompt = Prompt.objects.create(
        title=f"{original.title} (tool feedback)",
        content=mutated_text,
        type=original.type,
        source="tool-feedback",
        parent=original,
    )
    PromptMutationLog.objects.create(
        original_prompt=original,
        mutated_text=mutated_text,
        mode="tool_feedback",
    )

    AssistantPromptLink.objects.filter(prompt=original).update(prompt=new_prompt)
    assistant.system_prompt = new_prompt
    assistant.save(update_fields=["system_prompt"])

    if message:
        AssistantReflectionLog.objects.create(
            assistant=assistant,
            title="Tool Feedback Reflection",
            summary=message,
            raw_prompt=original.content,
            category="behavior",
        )

    return new_prompt
