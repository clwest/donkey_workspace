import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    AutoPoeticCodexEmergenceEngine,
    MythOSIdentityForkManager,
    RecursiveIntelligenceGrowthNetwork,
)


class Phase181ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A1")
        self.other = Assistant.objects.create(name="A2")
        self.memory1 = SwarmMemoryEntry.objects.create(title="m1", content="c1")
        self.memory2 = SwarmMemoryEntry.objects.create(title="m2", content="c2")

    def test_auto_poetic_codex_emergence_engine(self):
        engine = AutoPoeticCodexEmergenceEngine.objects.create(
            initiating_assistant=self.assistant,
            ritual_trigger_chain={},
            emergent_codex_title="Codex",
            symbolic_seed_summary="seed",
        )
        engine.memory_braid_source.add(self.memory1, self.memory2)
        self.assertEqual(engine.memory_braid_source.count(), 2)
        self.assertEqual(engine.initiating_assistant, self.assistant)

    def test_identity_fork_manager(self):
        fork = MythOSIdentityForkManager.objects.create(
            original_assistant=self.assistant,
            forked_identity_id="fork1",
            divergence_event="event",
            belief_delta_vector={},
            symbolic_resonance_score=0.5,
        )
        self.assertEqual(fork.original_assistant, self.assistant)
        self.assertEqual(fork.forked_identity_id, "fork1")

    def test_recursive_intelligence_growth_network(self):
        network = RecursiveIntelligenceGrowthNetwork.objects.create(
            network_id="net",
            codex_exchange_pathways={},
            belief_growth_log="log",
            mutation_cluster_hash="h",
        )
        network.participating_assistants.add(self.assistant, self.other)
        self.assertEqual(network.participating_assistants.count(), 2)
