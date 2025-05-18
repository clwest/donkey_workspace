# prompts/utils/embeddings.py

from embeddings.helpers.helpers_processing import generate_embedding
from typing import Optional, List
import logging

logger = logging.getLogger("prompts")


def get_prompt_embedding(text: str) -> Optional[List[float]]:
    """
    Generate an embedding vector for a given prompt text using the core embedding system.

    Args:
        text: Prompt text to embed.

    Returns:
        List of floats representing the embedding, or None if generation failed.
    """
    if not text or not text.strip():
        logger.warning("Empty or blank text received for embedding.")
        return None

    try:
        return generate_embedding(text)
    except Exception as e:
        logger.error(f"Failed to generate prompt embedding: {e}", exc_info=True)
        return None
