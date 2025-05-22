import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    CollaborationThread,
    DelegationStream,
    MythflowInsight,
    SwarmMemoryEntry,
)


class Phase61ModelTest(TestCase):
    def setUp(self):
        self.a1 = Assistant.objects.create(name="A1")
        self.a2 = Assistant.objects.create(name="A2")
        self.mem = SwarmMemoryEntry.objects.create(title="M", content="c")

    def test_collaboration_thread(self):
        thread = CollaborationThread.objects.create(
            title="T",
            narrative_focus="focus",
            symbolic_tags={},
            originating_memory=self.mem,
        )
        thread.participants.add(self.a1, self.a2)
        self.assertEqual(thread.participants.count(), 2)
        self.assertTrue(thread.active)

    def test_delegation_stream(self):
        stream = DelegationStream.objects.create(
            stream_name="S",
            source_assistant=self.a1,
            target_assistant=self.a2,
            symbolic_context={},
            task_rationale="r",
        )
        self.assertEqual(stream.stream_status, "pending")

    def test_mythflow_insight(self):
        thread = CollaborationThread.objects.create(
            title="T2",
            narrative_focus="x",
            symbolic_tags={},
        )
        thread.participants.add(self.a1)
        insight = MythflowInsight.objects.create(
            thread=thread,
            generated_by=self.a1,
            insight_summary="sum",
        )
        self.assertFalse(insight.symbolic_shift_detected)
