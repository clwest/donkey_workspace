import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from utils.prompt_helpers import generate_codex_reflection_prompt


def test_generate_codex_reflection_prompt():
    prompt = generate_codex_reflection_prompt(
        clause_text="Assistants must reflect after major symbolic changes.",
        campaign_outcome="approved by consensus (4–1 vote)",
        assistant_vote="supported",
        assistant_archetype="Codex Strategist",
        tone_model="philosophical",
    )
    assert "Clause:" in prompt
    assert "Campaign outcome" in prompt
    assert "Assistants must reflect" in prompt
    assert "Codex Strategist" in prompt

