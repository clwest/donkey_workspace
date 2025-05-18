# mcp_core/utils/auto_tag_from_embedding.py

import logging
from embeddings.helpers.helpers_processing import generate_embedding
from mcp_core.models import Tag
from embeddings.helpers.helpers_io import search_similar_embeddings_for_model

logger = logging.getLogger("mcp_core")


def auto_tag_from_embedding(text: str, top_k: int = 5) -> list[str]:
    """
    Generate tags from an embedding similarity search.

    Args:
        text: The input text to tag.
        top_k: Number of tags to return.

    Returns:
        A list of tag slugs (or names) most semantically similar to the text.
    """
    if not text or not text.strip():
        logger.warning("🛑 Empty text provided to auto_tag_from_embedding.")
        return []

    try:
        embedding = generate_embedding(text)
        if not embedding:
            logger.error("❌ Embedding generation failed.")
            return []

        results = search_similar_embeddings_for_model(
            query_vector=embedding,
            model_class=Tag,
            vector_field_name="embedding",
            content_field_name="name",  # or use "description" if preferred
            top_k=top_k,
        )

        tags = [r["content"] for r in results]
        return tags

    except Exception as e:
        logger.error(f"💥 Error in auto_tag_from_embedding: {e}", exc_info=True)
        return []
