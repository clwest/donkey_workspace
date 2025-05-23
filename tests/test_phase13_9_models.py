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
    assistant = Assistant.objects.create(name="Alpha", specialty="sage")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")

    chamber = SymbolicFeedbackChamber.objects.create(
        chamber_title="Chamber",
        participant_ids=["u1"],
        codex_review=codex,
        ritual_scorecards={"u1": 1},
    )
    chamber.memory_archive.add(memory)

    amplifier = MultiAgentDialogueAmplifier.objects.create(
        amplifier_title="Amp",
        active_codex=codex,
        layered_response="r",
        symbolic_resonance_score=0.9,
    )
    amplifier.agents_involved.add(assistant)

    sequence = MythicResolutionSequence.objects.create(
        assistant=assistant,
        resolution_steps=["end"],
        codex_closure_state="closed",
        legacy_artifacts={"key": "v"},
        symbolic_final_score=1.0,
    )

    assert chamber.codex_review == codex
    assert amplifier.agents_involved.count() == 1
    assert sequence.symbolic_final_score == 1.0
