# prompts/utils/mutation.py

from typing import Optional
from prompts.models import Prompt, PromptMutationLog
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
