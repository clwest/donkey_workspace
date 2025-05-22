import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmTribunalCase,
    RestorativeMemoryAction,
    ReputationRegenerationEvent,
)


class Phase501ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_swarm_tribunal_case(self):
        case = SwarmTribunalCase.objects.create(
            issue_type="constraint", reflective_summary="s"
        )
        case.involved_assistants.add(self.assistant)
        case.memory_evidence.add(self.memory)
        self.assertEqual(case.involved_assistants.count(), 1)
        self.assertEqual(case.memory_evidence.count(), 1)
        self.assertEqual(case.verdict, "undecided")

    def test_restorative_memory_action(self):
        action = RestorativeMemoryAction.objects.create(
            initiating_assistant=self.assistant,
            damaged_memory=self.memory,
            reformation_notes="fix",
        )
        self.assertFalse(action.resolved)
        self.assertEqual(action.damaged_memory, self.memory)

    def test_reputation_regeneration_event(self):
        event = ReputationRegenerationEvent.objects.create(
            assistant=self.assistant,
            reflection_cycle_reference=self.memory,
            change_summary="improved",
            symbolic_rebirth_tags={},
            regenerated_score=1.0,
        )
        self.assertEqual(event.assistant, self.assistant)
        self.assertEqual(event.regenerated_score, 1.0)
