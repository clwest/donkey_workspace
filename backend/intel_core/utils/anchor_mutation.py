from typing import List
from utils.llm_router import call_llm


def build_mutation_prompt(anchor: str, context: str) -> List[dict]:
    """Return chat messages prompting LLM to suggest alternate anchors."""
    system = (
        "You are a glossary curator helping an AI assistant maintain terminology."
    )
    user = (
        f"A glossary anchor failed to ground: \"{anchor}\". "
        "It appears in reflections but has no matching documents.\n\n"
        "Please suggest 2-3 alternate glossary terms or phrases that better match the assistant's context. "
        "Use synonyms or paraphrased variants.\n\n"
        f"Reflection Context:\n{context}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def suggest_anchor_mutations(anchor: str, context: str) -> str:
    """Call LLM to get anchor mutation suggestions."""
    messages = build_mutation_prompt(anchor, context)
    return call_llm(messages, model="gpt-4o", temperature=0.5, max_tokens=150)
