# prompts/utils/mutation.py

from typing import Optional
from prompts.models import Prompt
from prompts.utils.embeddings import get_prompt_embedding
from embeddings.helpers.helpers_io import save_embedding
import logging
from utils.llm_router import call_llm

logger = logging.getLogger("prompts")


MUTATION_MODES = {
    "clarify": "Rewrite this prompt to be clearer and easier to understand, but keep the meaning the same.",
    "expand": "Add helpful context, clarification, or examples to this prompt without changing the original meaning.",
    "shorten": "Make this prompt shorter and more concise, while keeping the core idea.",
    "formalize": "Rewrite this prompt in a more formal and professional tone.",
    "casualize": "Rewrite this prompt to sound more casual and relaxed.",
    "convertToBulletPoints": "Reformat this prompt into clear, concise bullet points while keeping all the key information.",
}

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

    instruction = MUTATION_MODES.get(mode)
    if instruction is None:
        logger.warning("Unknown mutation mode '%s'; falling back to 'clarify'", mode)
        instruction = MUTATION_MODES["clarify"]
        mode = "clarify"

    system_prompt = f"You are a prompt mutation engine. Mutation type: {mode}. {instruction}"
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
        except Prompt.DoesNotExist:
            logger.warning(f"❌ Prompt ID not found for embedding: {prompt_id}")

    return result
