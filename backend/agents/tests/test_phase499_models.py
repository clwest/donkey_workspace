import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SymbolicAlliance,
    SwarmCodex,
    SymbolicLawEntry,
    RitualArchiveEntry,
    SwarmMemoryEntry,
)


class Phase499ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.alliance = SymbolicAlliance.objects.create(
            name="Alliance",
            aligned_beliefs={},
            shared_purpose_vector={},
        )
        self.alliance.founding_assistants.add(self.assistant)

    def test_swarm_codex(self):
        codex = SwarmCodex.objects.create(
            title="C",
            created_by=self.assistant,
            symbolic_domain="knowledge",
        )
        codex.governing_alliances.add(self.alliance)
        self.assertEqual(codex.governing_alliances.count(), 1)

    def test_symbolic_law_entry(self):
        codex = SwarmCodex.objects.create(
            title="C2",
            created_by=self.assistant,
            symbolic_domain="diplomacy",
        )
        law = SymbolicLawEntry.objects.create(
            codex=codex,
            description="desc",
            symbolic_tags={},
            derived_from_memory=self.memory,
            enforcement_scope="guild",
        )
        self.assertEqual(law.codex, codex)
        self.assertEqual(law.derived_from_memory, self.memory)

    def test_ritual_archive_entry(self):
        codex = SwarmCodex.objects.create(
            title="C3",
            created_by=self.assistant,
            symbolic_domain="transformation",
        )
        archive = RitualArchiveEntry.objects.create(
            name="R",
            related_memory=self.memory,
            ceremony_type="init",
            symbolic_impact_summary="s",
            locked_by_codex=codex,
        )
        archive.participant_assistants.add(self.assistant)
        self.assertEqual(archive.locked_by_codex, codex)
        self.assertEqual(archive.participant_assistants.count(), 1)
