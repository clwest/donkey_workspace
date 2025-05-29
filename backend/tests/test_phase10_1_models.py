import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, SwarmCodex
from simulation.models import MythScenarioSimulator, MythflowSession, SymbolicDialogueExchange


def test_phase10_1_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant)

    sim = MythScenarioSimulator.objects.create(
        simulation_title="title",
        initiating_entity=assistant,
        selected_archetypes={"hero": 1},
        narrative_goals="goal",
    )

    session = MythflowSession.objects.create(session_name="S", active_scenario=sim)
    session.participants.add(assistant)
    session.memory_trace.add(mem)
    session.live_codex_context.add(codex)

    msg = SymbolicDialogueExchange.objects.create(
        session=session,
        sender=assistant,
        message_content="hi",
        symbolic_intent={"greet": True},
        codex_alignment_score=0.9,
    )

    assert session.participants.count() == 1
    assert session.live_codex_context.count() == 1
    assert msg.session == session
