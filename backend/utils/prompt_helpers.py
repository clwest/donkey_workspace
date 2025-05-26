"""Prompt helper utilities."""


def generate_codex_reflection_prompt(
    clause_text: str,
    campaign_outcome: str,
    assistant_vote: str,
    assistant_archetype: str,
    tone_model: str,
) -> str:
    """Return a formatted codex reflection prompt."""
    return (
        f"Clause:\n\"{clause_text}\"\n"
        f"Campaign outcome: {campaign_outcome}\n"
        f"Assistant vote: {assistant_vote}\n\n"
        f"Reflect aloud in the tone of {tone_model} {assistant_archetype}:\n"
        "1. How does this clause resonate with your current beliefs?\n"
        "2. Should the clause evolve, fork, or be archived?\n"
        "3. Does it match your memory and mythic alignment?"
    )

