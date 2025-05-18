# prompts/utils/mutation.py

from openai import OpenAI
from typing import Optional, List
from prompts.models import Prompt
from prompts.utils.embeddings import get_prompt_embedding
from embeddings.helpers.helpers_io import save_embedding
import logging

logger = logging.getLogger("prompts")

client = OpenAI()

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
    text: str, mode: str = "clarify", prompt_id: Optional[str] = None
) -> str:
    """Mutate a prompt with a specified style using OpenAI.

    Args:
        text: The original prompt text to transform.
        mode: Key specifying the mutation style defined in ``MUTATION_MODES``.
        prompt_id: Optional ID of a ``Prompt`` whose embedding should be
            updated after mutation.

    Returns:
        The mutated prompt text.

    Side Effects:
        When ``prompt_id`` is provided and the corresponding ``Prompt`` exists,
        an embedding for the mutated text is generated and saved. This may
        trigger embedding-related storage operations.
    """
    instruction = MUTATION_MODES.get(mode, MUTATION_MODES["clarify"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": text},
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    result = response.choices[0].message.content.strip()

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
