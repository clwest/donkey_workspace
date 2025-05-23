import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    EpistemicCurrent,
    FeedbackAnchorNode,
    KnowledgeEcologyMap,
)


def test_epistemic_models_create(db):
    a1 = Assistant.objects.create(name="A", specialty="t")
    a2 = Assistant.objects.create(name="B", specialty="t")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    current = EpistemicCurrent.objects.create(
        source=a1,
        content_summary="s",
        symbolic_tags={"t": 1},
        current_strength=0.5,
    )
    current.targets.add(a2)

    anchor = FeedbackAnchorNode.objects.create(
        linked_memory=mem,
        insight_yield="y",
    )
    anchor.assistants_reflected.add(a1, a2)

    km = KnowledgeEcologyMap.objects.create(
        scope="assistant",
        symbolic_regions={},
        pressure_zones={},
    )
    km.active_currents.add(current)

    assert current.pk
    assert anchor.pk
    assert km.pk

