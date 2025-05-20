# utils/llm.py

from dotenv import load_dotenv
load_dotenv()

# Kept for backward compatibility but routed through the new llm_router
from utils.llm_router import call_llm, DEFAULT_MODEL


def call_gpt4(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 512, temperature: float = 0.4) -> str:
    """Simple wrapper to maintain existing imports."""
    messages = [{"role": "user", "content": prompt}]
    return call_llm(messages, model=model, max_tokens=max_tokens, temperature=temperature)


