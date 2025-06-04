import json
import logging
from utils.llm_router import call_llm

logger = logging.getLogger("embeddings")


def generate_tags_for_memory(content: str, max_tags: int = 5) -> list[str]:
    """Return LLM-generated tag names for the given content."""
    prompt = f"""You are an AI tagger. Analyze the following content and return up to {max_tags} short, descriptive tags.

Content:
\"\"\"
{content}
\"\"\"

Return the tags as a JSON list of lowercase strings, like:
[\"reflection\", \"architecture\", \"memory\", \"decision\"]
"""

    response = ""
    try:
        response = call_llm([{"role": "user", "content": prompt}], max_tokens=150)
        # logger.debug(f"🧪 Raw tag LLM response:\n{response!r}")

        # Strip Markdown code block if it exists
        if response.strip().startswith("```"):
            response = response.strip().strip("```").strip("json").strip()

        tags = json.loads(response)

        if not isinstance(tags, list):
            raise ValueError("Response was not a list")

        return [str(tag).lower() for tag in tags]

    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse tags: {e}", exc_info=True)
        logger.debug(f"🧪 Failed tag content:\n{response!r}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error generating tags: {e}", exc_info=True)
        return []
