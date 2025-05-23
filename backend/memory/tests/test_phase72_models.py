import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models.lore import SwarmMemoryEntry
from memory.models import BraidedMemoryStrand, ContinuityAnchorPoint
from memory.utils.anamnesis_engine import run_anamnesis_retrieval


class Phase72ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_braided_memory_strand(self):
        strand = BraidedMemoryStrand.objects.create(
            primary_assistant=self.assistant,
            integration_notes="notes",
            symbolic_alignment_score=0.5,
        )
        strand.alternate_sources.add(self.mem)
        self.assertEqual(strand.primary_assistant, self.assistant)
        self.assertEqual(strand.alternate_sources.count(), 1)

    def test_continuity_anchor_point(self):
        anchor = ContinuityAnchorPoint.objects.create(
            label="root",
            assistant=self.assistant,
            anchor_memory=self.mem,
            mythic_tag="origin",
            symbolic_signature="sig",
        )
        self.assertEqual(anchor.anchor_memory, self.mem)

    def test_anamnesis_retrieval(self):
        strand = BraidedMemoryStrand.objects.create(
            primary_assistant=self.assistant,
            integration_notes="n",
            symbolic_alignment_score=1.0,
        )
        strand.alternate_sources.add(self.mem)
        ContinuityAnchorPoint.objects.create(
            label="r",
            assistant=self.assistant,
            anchor_memory=self.mem,
            mythic_tag="t",
            symbolic_signature="s",
        )
        result = run_anamnesis_retrieval(self.assistant)
        self.assertIn("summary", result)
        self.assertEqual(result["recovery_score"], 2)

