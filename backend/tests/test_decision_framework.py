import pytest
pytest.importorskip("django")

from assistants.models import Assistant, ConscienceModule, DecisionFramework


def test_decision_framework_creation(db):
    assistant = Assistant.objects.create(name="Test", specialty="testing")
    conscience = ConscienceModule.objects.create(
        assistant=assistant,
        core_values=["honesty"],
        ethical_constraints={},
    )

    decision = DecisionFramework.objects.create(
        assistant=assistant,
        linked_conscience=conscience,
        myth_weight_map={"1": 0.6},
        scenario_description="Test scenario",
        selected_strategy="A",
    )

    assert decision.pk
    assert decision.linked_conscience == conscience
