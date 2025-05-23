import pytest

pytest.importorskip("django")

from assistants.models import Assistant, CodexLinkedGuild
from agents.models import (
    SwarmCodex,
    EncodedRitualBlueprint,
    GuildCurrencyExchangeHub,
    BeliefTokenMarket,
    RitualGrantSystem,
)


def test_phase15_4_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    guild1 = CodexLinkedGuild.objects.create(guild_name="G1", codex=codex)
    guild2 = CodexLinkedGuild.objects.create(guild_name="G2", codex=codex)

    hub = GuildCurrencyExchangeHub.objects.create(
        guild=guild1,
        exchange_rates={"G2": 1.5},
        symbolic_reserve=50.0,
    )
    hub.partner_guilds.add(guild2)

    market = BeliefTokenMarket.objects.create(
        codex=codex,
        listed_tokens={"T": 1},
        trade_history=[],
        liquidity_pool=75.0,
    )

    blueprint = EncodedRitualBlueprint.objects.create(name="R", encoded_steps=[])

    grant = RitualGrantSystem.objects.create(
        assistant=assistant,
        funded_ritual=blueprint,
        funding_source=hub,
        symbolic_outcome_summary="S",
        granted_tokens=10.0,
    )

    assert hub.partner_guilds.count() == 1
    assert market.codex == codex
    assert grant.funding_source == hub
