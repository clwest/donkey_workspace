from dotenv import load_dotenv
from typing import List
import logging
from utils.llm_router import call_llm

load_dotenv()
logger = logging.getLogger("prompts")


def reduce_tokens(text: str, model: str = "gpt-4") -> str:
    try:
        return call_llm(
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that shortens prompts by preserving intent and function while reducing token length.",
                },
                {"role": "user", "content": text},
            ],
            model=model,
            temperature=0.3,
        )
    except Exception as e:
        return f"[Token reduction failed: {e}]"


PROMPT_ASSISTANT_INSTRUCTION = (
    "You are a Prompt Creation Assistant. Based on the user's idea, generate a complete, clean, and useful system prompt "
    "for use with a large language model. The output should be precise, well-formatted, and designed to optimize performance. "
    "Avoid extra explanations or unnecessary wrapping."
)


def generate_prompt_from_idea(idea: str) -> str:
    """
    Use OpenAI to generate a clean system prompt from a user-provided idea.
    """
    try:
        return call_llm(
            [
                {"role": "system", "content": PROMPT_ASSISTANT_INSTRUCTION},
                {"role": "user", "content": idea},
            ],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=800,
        )
    except Exception as e:
        logger.error(f"Failed to generate prompt from idea: {e}", exc_info=True)
        return ""


def extract_title_from_prompt(content: str) -> str:
    lines = content.strip().splitlines()
    for line in lines:
        if line.strip():
            return line.strip().replace("**", "").strip(":")
    return "AI-Generated Prompt"


def complete_chat(
    system: str,
    user: str,
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 800,
) -> str:
    try:
        return call_llm(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        logger.error(f"❌ complete_chat failed: {e}", exc_info=True)
        return ""


def reflect_on_prompt(text: str) -> str:
    """Analyze a problematic prompt and produce clarification advice."""
    try:
        return call_llm(
            [
                {
                    "role": "system",
                    "content": "You clarify vague or failing prompts by suggesting concise improvements.",
                },
                {"role": "user", "content": text},
            ],
            model="gpt-4o",
            temperature=0,
            max_tokens=150,
        )
    except Exception as e:  # pragma: no cover - network
        logger.error(f"❌ reflect_on_prompt failed: {e}", exc_info=True)
        return ""
