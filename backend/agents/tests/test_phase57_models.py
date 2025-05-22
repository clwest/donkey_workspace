import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    ArchetypeEvolutionEvent,
    CodexSymbolReconciliation,
)


class Phase57ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_archetype_evolution_event(self):
        event = ArchetypeEvolutionEvent.objects.create(
            assistant=self.assistant,
            previous_archetype="sage",
            new_archetype="oracle",
            trigger_memory=self.memory,
            symbolic_justification="vision",
        )
        self.assertEqual(event.assistant, self.assistant)
        self.assertEqual(event.new_archetype, "oracle")

    def test_codex_symbol_reconciliation(self):
        rec = CodexSymbolReconciliation.objects.create(
            conflicting_symbol="dragon",
            proposed_resolution="merge meaning",
        )
        rec.affected_codices.add(self.codex)
        self.assertEqual(rec.affected_codices.count(), 1)
        self.assertFalse(rec.resolution_accepted)
