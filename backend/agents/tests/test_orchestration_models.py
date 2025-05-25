import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import AssistantOrchestrationEvent, OrchestrationTimelineSnapshot, RitualRewiringProposal


class OrchestrationModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Beta")

    def test_event_creation(self):
        ev = AssistantOrchestrationEvent.objects.create(
            assistant=self.assistant,
            event_type="task",
            started_at="2025-01-01T00:00:00Z",
        )
        self.assertEqual(ev.assistant, self.assistant)

    def test_snapshot_creation(self):
        ev = AssistantOrchestrationEvent.objects.create(
            assistant=self.assistant,
            event_type="task",
            started_at="2025-01-01T00:00:00Z",
        )
        snap = OrchestrationTimelineSnapshot.objects.create(snapshot_date="2025-01-01")
        snap.events.add(ev)
        self.assertEqual(snap.events.count(), 1)

    def test_rewire_proposal(self):
        target = Assistant.objects.create(name="Gamma")
        prop = RitualRewiringProposal.objects.create(
            initiator=self.assistant,
            receiver=target,
            context_clause="demo",
        )
        self.assertEqual(prop.receiver, target)

