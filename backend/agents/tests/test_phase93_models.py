import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    PurposeGraftRecord,
    SuccessionRitualEvent,
    ReincarnationTreeNode,
    SwarmMemoryEntry,
)


class Phase93ModelTest(TestCase):
    def setUp(self):
        self.a1 = Assistant.objects.create(name="A1")
        self.a2 = Assistant.objects.create(name="A2")
        self.mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_purpose_graft_record(self):
        rec = PurposeGraftRecord.objects.create(
            source_assistant=self.a1,
            target_assistant=self.a2,
            grafted_traits={"focus": "x"},
            symbolic_justification="legacy",
            narrative_epoch="era",
        )
        self.assertEqual(rec.source_assistant, self.a1)
        self.assertEqual(rec.target_assistant, self.a2)

    def test_succession_ritual_event(self):
        ritual = SuccessionRitualEvent.objects.create(
            outgoing_archetype="sage",
            successor_assistant=self.a2,
            ritual_steps=["step1"],
            confirmed=True,
        )
        ritual.memory_basis.add(self.mem)
        self.assertTrue(ritual.confirmed)
        self.assertEqual(list(ritual.memory_basis.all())[0], self.mem)

    def test_reincarnation_tree_node(self):
        node = ReincarnationTreeNode.objects.create(
            node_name="root",
            assistant=self.a1,
            symbolic_signature={"sig": 1},
            phase_index="9.3",
        )
        self.assertEqual(node.node_name, "root")
        self.assertEqual(node.assistant, self.a1)

