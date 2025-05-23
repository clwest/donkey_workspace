import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    MythicAfterlifeRegistry,
    ContinuityEngineNode,
    ArchetypeMigrationGate,
)


class Phase95ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Beta", specialty="ritual")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(
            title="Codex", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_afterlife_registry(self):
        reg = MythicAfterlifeRegistry.objects.create(
            assistant=self.assistant,
            retirement_codex=self.codex,
            archived_traits={"x": 1},
            reincarnation_ready=True,
        )
        reg.memory_links.add(self.memory)
        self.assertEqual(reg.retirement_codex, self.codex)
        self.assertEqual(reg.memory_links.count(), 1)

    def test_continuity_engine_node(self):
        node = ContinuityEngineNode.objects.create(
            linked_assistant=self.assistant,
            preserved_belief_vector={"p": 1},
            continuity_trace="t",
            transformation_trigger="e",
        )
        self.assertEqual(node.linked_assistant, self.assistant)
        self.assertEqual(node.preserved_belief_vector["p"], 1)

    def test_migration_gate(self):
        gate = ArchetypeMigrationGate.objects.create(
            gate_name="Gate",
            initiating_entity=self.assistant,
            migration_path={"from": "a", "to": "b"},
            transfer_protocol="p",
            anchor_codex=self.codex,
        )
        self.assertEqual(gate.anchor_codex, self.codex)
        self.assertEqual(gate.gate_name, "Gate")
