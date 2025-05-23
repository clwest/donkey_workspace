import pytest

pytest.importorskip("django")

from assistants.models import Assistant, CodexLinkedGuild
from agents.models import (
    SwarmCodex,
    EncodedRitualBlueprint,
    RitualIncentiveSystem,
    SymbolicFundingProtocol,
)


def test_phase15_3_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    blueprint = EncodedRitualBlueprint.objects.create(name="R", encoded_steps=[])

    reward = RitualIncentiveSystem.objects.create(
        ritual=blueprint,
        assistant=assistant,
        user_id="u1",
        symbolic_reward=2.5,
        codex_tags={"t": 1},
    )

    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    guild = CodexLinkedGuild.objects.create(guild_name="G", codex=codex)

    protocol = SymbolicFundingProtocol.objects.create(
        guild=guild,
        symbolic_reserve=100.0,
        proposed_allocations={"p": 1},
        contributor_votes={"u1": 1},
        approved_projects={"a": 1},
    )

    assert reward.assistant == assistant
    assert protocol.guild == guild
