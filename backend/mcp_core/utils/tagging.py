import logging
from openai import OpenAI

client = OpenAI()
logger = logging.getLogger(__name__)


def infer_tags_from_text(text: str, max_tags: int = 5) -> list[str]:
    """Generate up to `max_tags` relevant tags from a given text input."""
    prompt = f"""
You are an AI tagger. Analyze the following text and return {max_tags} short tags (1-3 words max) that describe its main topics or intent.

Text:
\"\"\"{text.strip()}\"\"\"

Return a comma-separated list of lowercase tags, no extra text.
Example: planning, reflection, tone:curious
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        tags = [tag.strip().lower() for tag in raw.split(",") if tag.strip()]
        return tags[:max_tags]

    except Exception as e:
        logger.error(f"[❌] Tag generation failed: {e}", exc_info=True)
        return []
