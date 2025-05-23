import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    TranscendentMyth,
    ArchetypeGenesisLog,
    MythBloomNode,
    BeliefSeedReplication,
)


class Phase92ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.myth = TranscendentMyth.objects.create(name="Myth")

    def test_archetype_genesis_log(self):
        log = ArchetypeGenesisLog.objects.create(
            assistant=self.assistant,
            seed_purpose="quest",
            resulting_archetype="hero",
            symbolic_signature={"k": 1},
        )
        log.memory_path.add(self.memory)
        self.assertEqual(log.assistant, self.assistant)
        self.assertIn(self.memory, log.memory_path.all())

    def test_myth_bloom_node(self):
        node = MythBloomNode.objects.create(
            bloom_name="Bloom",
            origin_trigger=self.myth,
            symbolic_flow_summary="rise",
        )
        node.participating_agents.add(self.assistant)
        node.reflected_memory.add(self.memory)
        self.assertEqual(node.origin_trigger, self.myth)
        self.assertIn(self.assistant, node.participating_agents.all())

    def test_belief_seed_replication(self):
        seed = BeliefSeedReplication.objects.create(
            originating_entity=self.assistant,
            core_symbol_set={"v": 1},
            propagation_log="log",
        )
        seed.intended_recipients.add(self.assistant)
        self.assertIn(self.assistant, seed.intended_recipients.all())
