import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    CodexCurrencyModule,
    SymbolicInfluenceLedger,
    BeliefContributionMarketplace,
)


def test_phase15_2_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")

    module = CodexCurrencyModule.objects.create(
        codex=codex,
        mutation_impact_score=1.0,
        ritual_weight_multiplier=0.5,
        symbolic_value_curve={"phase": 1},
    )

    ledger = SymbolicInfluenceLedger.objects.create(
        user_id="u1",
        assistant=assistant,
        codex_transactions={"c": 1},
        ritual_scores={"r": 2},
        influence_balance=10.0,
    )
    ledger.memory_contributions.add(memory)

    market = BeliefContributionMarketplace.objects.create(
        proposal_title="P",
        proposer=assistant,
        staked_tokens={"t": 1},
        endorsed_rituals={"e": 1},
        ranked_insights=[{"i": 1}],
    )

    assert module.codex == codex
    assert ledger.memory_contributions.count() == 1
    assert market.proposer == assistant
