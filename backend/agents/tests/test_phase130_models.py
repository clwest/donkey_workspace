import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    MemoryInheritanceSeed,
    PersonalCodexAnchor,
    RitualContractBinding,
    ReincarnationTreeNode,
    BeliefVectorDelta,
)
from django.utils import timezone


class Phase130ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.memory = SwarmMemoryEntry.objects.create(title="M", content="c")
        self.codex = SwarmCodex.objects.create(
            title="Codex", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_models_create(self):
        seed = MemoryInheritanceSeed.objects.create(
            user_id="u1", narrative_path="p", symbolic_tags={}
        )
        seed.onboarding_memory.add(self.memory)

        anchor = PersonalCodexAnchor.objects.create(
            user_id="u1", codex=self.codex, symbolic_statements={}, anchor_strength=0.5
        )

        contract = RitualContractBinding.objects.create(
            assistant=self.assistant,
            user_id="u1",
            contract_terms="t",
            codex_link=self.codex,
        )
        contract.shared_memory.add(self.memory)

        node = ReincarnationTreeNode.objects.create(
            node_name="root",
            assistant=self.assistant,
            symbolic_signature={},
            phase_index="13.0",
        )
        node.retained_memories.add(self.memory)

        delta = BeliefVectorDelta.objects.create(
            assistant=self.assistant, delta_vector={}, recorded_at=timezone.now()
        )

        self.assertEqual(seed.onboarding_memory.count(), 1)
        self.assertEqual(anchor.codex, self.codex)
        self.assertEqual(contract.shared_memory.count(), 1)
        self.assertEqual(node.assistant, self.assistant)
        self.assertEqual(delta.assistant, self.assistant)
