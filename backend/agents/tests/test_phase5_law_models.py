import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    AssistantPolity,
    SwarmCodex,
    SymbolicLawEntry,
    SwarmMemoryEntry,
)
from agents.models import MemoryTreaty, BeliefEnforcementScore
from agents.utils import evolve_symbolic_law


class Phase5LawModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha", specialty="law")
        self.memory = SwarmMemoryEntry.objects.create(title="Root", content="c")
        self.codex = SwarmCodex.objects.create(
            title="Codex", created_by=self.assistant, symbolic_domain="core"
        )
        law = SymbolicLawEntry.objects.create(
            codex=self.codex,
            description="Do no harm",
            symbolic_tags={"prime": True},
            enforcement_scope="global",
        )
        self.codex.active_laws.add(law)
        self.polity = AssistantPolity.objects.create(
            name="Polity", founding_codex=self.codex, core_purpose_statement="P"
        )

    def test_memory_treaty_creation(self):
        treaty = MemoryTreaty.objects.create(
            name="Accord",
            origin_memory=self.memory,
            terms="Peace",
            symbolic_tags={"peace": True},
        )
        treaty.participants.add(self.polity)
        self.assertTrue(treaty.active)
        self.assertEqual(treaty.participants.count(), 1)

    def test_belief_enforcement_score(self):
        score = BeliefEnforcementScore.objects.create(
            assistant=self.assistant,
            codex=self.codex,
            alignment_score=0.8,
            symbolic_compliance_log="ok",
        )
        self.assertGreaterEqual(score.alignment_score, 0)
        self.assertEqual(score.codex, self.codex)

    def test_evolve_symbolic_law_returns_memory(self):
        result = evolve_symbolic_law(self.codex)
        self.assertIn("memory_entry", result)
        self.assertTrue(
            SwarmMemoryEntry.objects.filter(id=result["memory_entry"]).exists()
        )
