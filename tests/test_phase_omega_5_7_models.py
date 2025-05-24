import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from metrics.models import (
    RitualReputationScore,
    CodexClauseVote,
    SwarmAlignmentIndex,
    AssistantBeliefVector,
    CodexClauseComplianceMap,
)


def test_phase_omega_5_7_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    rep = RitualReputationScore.objects.create(
        ritual_name="R",
        symbolic_tags=["t"],
        rating=0.8,
        assistant_approval_ratio=0.9,
        drift_reduction_effectiveness=0.7,
        outcome_quality=0.85,
    )
    vote = CodexClauseVote.objects.create(
        clause_id="c1",
        suggested_mutation="m",
        symbolic_tags=["x"],
        vote_choice="approve",
    )
    align = SwarmAlignmentIndex.objects.create(score=0.5, details={"x": 1})
    vec = AssistantBeliefVector.objects.create(assistant=assistant, vector=[1, 0])
    comp = CodexClauseComplianceMap.objects.create(clause_id="c1", compliance_ratio=0.9)

    assert rep.rating == 0.8
    assert vote.vote_choice == "approve"
    assert align.score == 0.5
    assert vec.assistant == assistant
    assert comp.clause_id == "c1"

