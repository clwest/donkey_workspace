import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SymbolicAnomalyEvent,
    BeliefCollapseRecoveryRitual,
    MultiverseLoopLink,
    SwarmMemoryEntry,
)


class Phase71ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_symbolic_anomaly_event(self):
        event = SymbolicAnomalyEvent.objects.create(
            assistant=self.assistant,
            anomaly_type="contradiction",
            detected_by="audit",
            symbolic_trace="trace",
        )
        event.memory_reference.add(self.memory)
        self.assertEqual(event.anomaly_type, "contradiction")
        self.assertEqual(event.memory_reference.count(), 1)

    def test_belief_collapse_recovery_ritual(self):
        ritual = BeliefCollapseRecoveryRitual.objects.create(
            assistant=self.assistant,
            initiating_memory=self.memory,
            collapse_type="paradox",
            ritual_steps={},
            restored_alignment={},
            successful=True,
        )
        self.assertTrue(ritual.successful)

    def test_multiverse_loop_link(self):
        loop = MultiverseLoopLink.objects.create(
            anchor_assistant=self.assistant,
            linked_timelines=["t1", "t2"],
            loop_reason="sync",
            echo_transfer_summary="done",
        )
        self.assertEqual(loop.linked_timelines, ["t1", "t2"])
