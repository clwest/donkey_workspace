import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    LegacyRingSlice,
    MemoryDendroMark,
    SymbolicLifespanModel,
    SwarmCodex,
    SwarmMemoryEntry,
)


class Phase940ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", specialty="x")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(title="c", created_by=self.assistant)

    def test_legacy_ring_slice(self):
        ring = LegacyRingSlice.objects.create(
            assistant=self.assistant,
            timestamp=django.utils.timezone.now(),
            symbolic_state={},
            purpose_score=0.5,
            role_tag="guide",
            reflection_notes="n",
        )
        self.assertEqual(ring.assistant, self.assistant)

    def test_memory_dendro_mark(self):
        mark = MemoryDendroMark.objects.create(
            memory=self.memory,
            dendro_layer="year1",
            symbolic_trigger_event="birth",
            growth_direction="outward",
            belief_delta=0.1,
        )
        self.assertEqual(mark.memory, self.memory)

    def test_symbolic_lifespan_model(self):
        model = SymbolicLifespanModel.objects.create(
            assistant=self.assistant,
            lifespan_curve={},
            archetype_pathway={},
            reflective_summary="s",
        )
        model.codex_participation.add(self.codex)
        self.assertIn(self.codex, model.codex_participation.all())
