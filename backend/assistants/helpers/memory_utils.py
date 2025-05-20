import json
import logging
import re
from django.utils.text import slugify
from mcp_core.models import Tag
from utils.llm_router import call_llm

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
        raw_output = call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
            temperature=0.2,
            max_tokens=150,
        )

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
