import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry
from simulation.models import (
    CinemythStoryline,
    PurposeLoopCinematicEngine,
    ReflectiveTheaterSession,
)


def test_phase10_7_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    story = CinemythStoryline.objects.create(
        authored_by=assistant,
        storyline_title="T",
        act_structure={"intro": 1},
        codex_alignment_vector={"v": 1},
    )
    story.memory_sources.add(mem)

    engine = PurposeLoopCinematicEngine.objects.create(
        linked_storyline=story,
        loop_condition="until done",
        symbolic_entropy_threshold=0.5,
    )

    session = ReflectiveTheaterSession.objects.create(
        viewer_identity="user",
        active_cinemyth=story,
        codex_interaction_log="log",
        symbolic_mood_map={},
        reflection_rating=0.8,
    )

    assert story.memory_sources.count() == 1
    assert engine.linked_storyline == story
    assert session.active_cinemyth == story
