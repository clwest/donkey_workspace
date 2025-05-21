import pytest
pytest.importorskip("django")

from assistants.models import Assistant, ConscienceModule
from assistants.utils.reflexive_epistemology import run_reflexive_belief_audit


def test_conscience_alignment_score(db):
    assistant = Assistant.objects.create(name="Test", specialty="testing")
    conscience = ConscienceModule.objects.create(
        assistant=assistant,
        core_values=["honesty", "collaboration"],
        ethical_constraints={"no_harm": True},
    )
    assistant.belief_vector = {"values": ["honesty", "innovation"]}
    assistant.save()

    result = run_reflexive_belief_audit(assistant)
    assert result["alignment_score"] == 0.5
    assert "innovation" in result["contradictions"]
