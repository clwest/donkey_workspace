import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    SymbolicFeedbackChamber,
    MultiAgentDialogueAmplifier,
    MythicResolutionSequence,
)


def test_phase13_9_models_create(db):
    assistant = Assistant.objects.create(name="A")
    memory = SwarmMemoryEntry.objects.create(title="m", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")

    chamber = SymbolicFeedbackChamber.objects.create(
        chamber_title="Ch",
        participant_ids=[assistant.id],
        codex_review=codex,
        ritual_scorecards={},
    )
    chamber.memory_archive.add(memory)

    amplifier = MultiAgentDialogueAmplifier.objects.create(
        amplifier_title="Amp",
        active_codex=codex,
        layered_response="r",
        symbolic_resonance_score=0.5,
    )
    amplifier.agents_involved.add(assistant)

    sequence = MythicResolutionSequence.objects.create(
        assistant=assistant,
        resolution_steps=[{"step": 1}],
        codex_closure_state="end",
        legacy_artifacts={},
        symbolic_final_score=1.0,
    )

    assert chamber.memory_archive.count() == 1
    assert amplifier.agents_involved.count() == 1
    assert sequence.symbolic_final_score == 1.0
