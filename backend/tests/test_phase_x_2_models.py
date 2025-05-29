import pytest

pytest.importorskip("django")

from assistants.models import Assistant, PersonalityCard, PersonalityDeck, SymbolicFeedbackRating, SwarmPromptEvolution
from agents.models import AgentFeedbackLog, SwarmCodex, SwarmMemoryEntry
from mcp_core.models import PromptUsageLog
from prompts.models import Prompt


def test_phase_x_2_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    prompt = Prompt.objects.create(title="P", content="t", source="s")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")

    card = PersonalityCard.objects.create(card_type="role", value="guide")
    deck = PersonalityDeck.objects.create(assistant=assistant, deck_name="D")
    deck.cards.add(card)

    prompt_log = PromptUsageLog.objects.create(
        prompt_slug="p", prompt_title="p", rendered_prompt="x", used_by="test"
    )
    agent = assistant.assigned_agents.create(name="ag", slug="ag", description="d", specialty="")
    agent_log = AgentFeedbackLog.objects.create(agent=agent, feedback_text="f")

    rating = SymbolicFeedbackRating.objects.create(
        assistant=assistant,
        prompt_log=prompt_log,
        agent_log=agent_log,
        memory_entry=memory,
        rating="👍",
    )

    evo = SwarmPromptEvolution.objects.create(
        parent_prompt=prompt,
        mutated_prompt_text="new",
        mutation_trace={"s": 1},
        codex_link=codex,
        success_score=0.5,
    )
    evo.mutated_by.add(assistant)

    assert deck.cards.count() == 1
    assert rating.assistant == assistant
    assert evo.codex_link == codex
