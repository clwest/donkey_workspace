import json
import logging
import re
from django.utils.text import slugify
from openai import OpenAI
from mcp_core.models import Tag

client = OpenAI()
logger = logging.getLogger(__name__)


def tag_text(content: str, max_tags: int = 5) -> list[Tag]:
    """
    Uses OpenAI to generate semantic tags for a block of text and returns Tag instances.
    """
    prompt = f"""
You are an AI tagger. Analyze the following memory content and return up to {max_tags} short, useful tags that describe its key topics, tone, or intent.

Content:
\"\"\"
{content}
\"\"\"

Return tags as a JSON list of lowercase strings like:
["planning", "reflection", "tone:curious"]
""".strip()

    raw_output = ""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150,
        )

        raw_output = response.choices[0].message.content.strip()

        # Remove triple backtick wrappers if present
        if raw_output.startswith("```"):
            raw_output = re.sub(
                r"^```.*?\n|\n```$", "", raw_output, flags=re.DOTALL
            ).strip()

        tag_names = json.loads(raw_output)
        tag_objects = []

        for name in tag_names:
            slug = slugify(name)
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
            tag_objects.append(tag)

        return tag_objects

    except Exception as e:
        logger.warning(f"⚠️ Failed to parse tag response: {e}")
        if raw_output:
            logger.debug(f"Raw tag response: {raw_output}")
        return []
