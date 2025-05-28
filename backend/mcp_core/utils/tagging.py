import logging

logger = logging.getLogger(__name__)


def infer_tags_from_text(text: str, max_tags: int = 5) -> list[str]:
    """Generate up to `max_tags` relevant tags from a given text input."""
    from utils.llm_router import call_llm

    prompt = f"""
You are an AI tagger. Analyze the following text and return {max_tags} short tags (1-3 words max) that describe its main topics or intent.

Text:
\"\"\"{text.strip()}\"\"\"

Return a comma-separated list of lowercase tags, no extra text.
Example: planning, reflection, tone:curious
"""

    try:
        raw = call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
            temperature=0.2,
        )
        tags = [tag.strip().lower() for tag in raw.split(",") if tag.strip()]
        return tags[:max_tags]

    except Exception as e:
        logger.error(f"[❌] Tag generation failed: {e}", exc_info=True)
        return []
