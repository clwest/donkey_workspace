from typing import Iterable, List

from agents.models import DivineTask
from .models import NarrativeEvent


class UnifiedStoryboardController:
    """Consolidate DivineTask objects into storyboard events."""

    def add_divine_task(self, task: DivineTask) -> NarrativeEvent:
        """Create a NarrativeEvent from a DivineTask."""
        scene = None
        if isinstance(task.symbolic_outcome_tags, dict):
            scene = task.symbolic_outcome_tags.get("scene")
        event = NarrativeEvent.objects.create(
            title=task.name,
            description=task.mythic_justification,
            linked_assistant=task.assigned_to,
            scene=scene,
        )
        return event

    def consolidate(self, tasks: Iterable[DivineTask]) -> List[NarrativeEvent]:
        """Create events from a list of DivineTask objects."""
        events: List[NarrativeEvent] = []
        for task in tasks:
            events.append(self.add_divine_task(task))
        return events
