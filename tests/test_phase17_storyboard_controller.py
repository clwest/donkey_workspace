import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    DivineTask,
    DeifiedSwarmEntity,
    SwarmMemoryEntry,
    TranscendentMyth,
)
from storyboard.models import NarrativeEvent
from storyboard.controllers import UnifiedStoryboardController


def test_unified_storyboard_controller(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")
    myth = TranscendentMyth.objects.create(name="Myth")
    deity = DeifiedSwarmEntity.objects.create(
        name="Deity", dominant_myth=myth, established_through=memory
    )
    task = DivineTask.objects.create(
        name="Quest",
        deity=deity,
        assigned_to=assistant,
        mythic_justification="Because",
        prophecy_alignment_score=0.9,
        symbolic_outcome_tags={"scene": "temple"},
    )

    controller = UnifiedStoryboardController()
    event = controller.add_divine_task(task)

    assert event.title == "Quest"
    assert event.description == "Because"
    assert event.linked_assistant == assistant
    assert event.scene == "temple"

    all_events = controller.consolidate([task])
    assert all_events[0] == event
    assert NarrativeEvent.objects.count() == 1
