# prompts/utils/mutation.py

from typing import Optional
from prompts.models import Prompt, PromptMutationLog
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from django.utils.text import slugify
from prompts.utils.embeddings import get_prompt_embedding
from embeddings.helpers.helpers_io import save_embedding
from prompts.utils.token_helpers import count_tokens
from prompts import mutation_styles
import logging
from utils.llm_router import call_llm

logger = logging.getLogger("prompts")


MAX_MUTATION_TOKENS = 8000  # Keep a small safety margin

def mutate_prompt(
    text: str,
    mode: str = "clarify",
    prompt_id: Optional[str] = None,
    tone: Optional[str] = None,
) -> str:
    """Mutate a prompt with a specified style using an LLM.

    Args:
        text: The original prompt text to transform.
        mode: Key specifying the mutation style defined in ``MUTATION_MODES``.
        prompt_id: Optional ID of a ``Prompt`` whose embedding should be
            updated after mutation.
        tone: Optional tone descriptor to apply to the mutated text.

    Returns:
        The mutated prompt text. If ``text`` is empty or ``mode`` is blank,
        the original ``text`` is returned and a warning is logged.

    Side Effects:
        When ``prompt_id`` is provided and the corresponding ``Prompt`` exists,
        an embedding for the mutated text is generated and saved. This may
        trigger embedding-related storage operations.
    """

    if not text or not mode:
        logger.warning("mutate_prompt called with empty text or missing mode")
        return text

    style = mutation_styles.get_style(mode)
    if style is None:
        logger.warning("Unknown mutation style '%s'; falling back to 'clarify'", mode)
        style = mutation_styles.get_style("clarify")
        mode = "clarify"

    system_prompt = style["system_prompt_template"].format(mutation_type=mode)
    if tone:
        system_prompt += f" Respond in a {tone} tone."

    result = call_llm(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        model="gpt-4o",
        temperature=0.7,
        max_tokens=1024,
    )
    tokens = count_tokens(result)

    if prompt_id:
        try:
            prompt_obj = Prompt.objects.get(id=prompt_id)
            vector = get_prompt_embedding(result)
            if vector:
                save_embedding(prompt_obj, vector)
            else:
                logger.warning(
                    f"❌ Skipping embedding for {prompt_obj.title} — empty or null vector"
                )

            PromptMutationLog.objects.create(
                original_prompt=prompt_obj,
                mutated_text=result,
                mode=mode,
                tone=tone or "",
                response_tokens=tokens,
            )
        except Prompt.DoesNotExist:
            logger.warning(f"❌ Prompt ID not found for embedding: {prompt_id}")

    return result


def mutate_prompt_from_reflection(
    assistant,
    reflection_log=None,
    reason: str = "",
) -> Prompt:
    """Generate a new system prompt for an assistant based on a reflection.

    This simplified implementation clones the assistant's existing prompt and
    appends a short note. It stores a ``PromptMutationLog`` linking the
    reflection and mutated prompt for lineage tracking.
    """

    source_prompt: Prompt | None = getattr(assistant, "system_prompt", None)
    if not source_prompt:
        return None

    mutated_text = f"{source_prompt.content}\n\n[Reflected mutation]"
    base_title = source_prompt.title
    if base_title.endswith(" (mutated)"):
        base_title = base_title[: -10]
    mutated_prompt = Prompt.objects.create(
        title=f"{base_title} (mutated)",
        content=mutated_text,
        source="reflection",
        parent=source_prompt,
    )

    PromptMutationLog.objects.create(
        original_prompt=source_prompt,
        mutated_text=mutated_text,
        mode="reflection",
        assistant=assistant,
        source_prompt=source_prompt,
        mutated_prompt=mutated_prompt,
        mutation_reason=reason,
        triggered_by_reflection=reflection_log,
    )

    assistant.system_prompt = mutated_prompt
    assistant.save(update_fields=["system_prompt"])
    return mutated_prompt


def fork_assistant_from_prompt(
    original: Assistant,
    new_prompt_text: str,
    *,
    reflection: AssistantReflectionLog | None = None,
    reason: str = "Hallucinated fallback during RAG query",
    allow_fork: bool = True,
    spawn_trigger: str = "manual",
) -> Assistant:
    """Fork ``original`` using ``new_prompt_text`` as the system prompt."""

    if not allow_fork:
        return original

    base_slug = slugify(f"{original.slug}-fork")
    existing = Assistant.objects.filter(slug=base_slug).first()
    if existing:
        return existing

    mutated_prompt = Prompt.objects.create(
        content=new_prompt_text,
        tone="directive",
    )

    child = Assistant.objects.create(
        name=f"{original.name} Fork",
        slug=base_slug,
        system_prompt=mutated_prompt,
        parent_assistant=original,
        specialty=original.specialty or "General AI Support",
        spawned_by=spawn_trigger,
    )

    print("🧠 Assistant Created:", child.name)
    print("🔗 Parent:", original.slug)
    print(f"⚙️ Trigger: {spawn_trigger}")

    PromptMutationLog.objects.create(
        original_prompt=original.system_prompt,
        mutated_text=new_prompt_text,
        mode="fork",
        assistant=original,
        source_prompt=original.system_prompt,
        mutated_prompt=mutated_prompt,
        mutation_reason=reason,
        triggered_by_reflection=reflection,
    )

    return child
