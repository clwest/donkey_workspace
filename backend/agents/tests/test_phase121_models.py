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
)


class Phase121ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.memory = SwarmMemoryEntry.objects.create(title="M", content="c")
        self.codex = SwarmCodex.objects.create(
            title="Codex", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_memory_inheritance_seed(self):
        seed = MemoryInheritanceSeed.objects.create(
            user_id="u1", narrative_path="p", symbolic_tags={}
        )
        seed.onboarding_memory.add(self.memory)
        self.assertEqual(seed.onboarding_memory.count(), 1)

    def test_personal_codex_anchor(self):
        anchor = PersonalCodexAnchor.objects.create(
            user_id="u1", codex=self.codex, symbolic_statements={}, anchor_strength=0.5
        )
        self.assertEqual(anchor.codex, self.codex)
        self.assertEqual(anchor.anchor_strength, 0.5)

    def test_ritual_contract_binding(self):
        contract = RitualContractBinding.objects.create(
            assistant=self.assistant,
            user_id="u1",
            contract_terms="t",
            codex_link=self.codex,
        )
        contract.shared_memory.add(self.memory)
        self.assertEqual(contract.shared_memory.count(), 1)
