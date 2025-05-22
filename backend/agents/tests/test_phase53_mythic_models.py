import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    AssistantPolity,
    SwarmCodex,
    MemoryTreaty,
    MythicArbitrationCase,
    TreatyBreachRitual,
    SymbolicSanction,
)


class Phase53MythicModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha", specialty="law")
        self.memory = SwarmMemoryEntry.objects.create(title="Root", content="c")
        self.codex = SwarmCodex.objects.create(
            title="Codex", created_by=self.assistant, symbolic_domain="core"
        )
        self.polity1 = AssistantPolity.objects.create(
            name="P1", founding_codex=self.codex, core_purpose_statement="p1"
        )
        self.polity2 = AssistantPolity.objects.create(
            name="P2", founding_codex=self.codex, core_purpose_statement="p2"
        )
        self.treaty = MemoryTreaty.objects.create(
            name="Accord",
            origin_memory=self.memory,
            terms="t",
            symbolic_tags={},
        )
        self.treaty.participants.add(self.polity1, self.polity2)

    def test_mythic_arbitration_case(self):
        case = MythicArbitrationCase.objects.create(
            conflict_treaty=self.treaty, initiating_polity=self.polity1
        )
        case.involved_polities.add(self.polity1, self.polity2)
        case.memory_evidence.add(self.memory)
        self.assertEqual(case.involved_polities.count(), 2)
        self.assertEqual(case.verdict, "pending")

    def test_treaty_breach_ritual(self):
        ritual = TreatyBreachRitual.objects.create(
            broken_treaty=self.treaty,
            violating_polity=self.polity2,
            breach_reason="x",
            triggered_ritual="shadow exile",
            reflective_outcome="loss",
        )
        self.assertEqual(ritual.violating_polity, self.polity2)
        self.assertEqual(ritual.triggered_ritual, "shadow exile")

    def test_symbolic_sanction(self):
        sanction = SymbolicSanction.objects.create(
            applied_to=self.assistant,
            codex=self.codex,
            symbolic_penalty="mute",
            duration_days=7,
            reason="breach",
        )
        self.assertFalse(sanction.lifted)
        self.assertEqual(sanction.duration_days, 7)
