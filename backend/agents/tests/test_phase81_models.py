import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    PurposeRadianceField,
    SymbolicGravityWell,
    MemoryHarmonicsPulse,
    SwarmMemoryEntry,
)


class Phase81ModelTests(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_radiance_field_creation(self):
        field = PurposeRadianceField.objects.create(
            assistant=self.assistant,
            emitted_frequency=1.0,
            narrative_alignment_vector={"a": 1},
            symbolic_beacon_tags=["x"],
            pulse_intensity=0.5,
        )
        self.assertEqual(field.assistant, self.assistant)
        self.assertGreater(field.emitted_frequency, 0)

    def test_gravity_well_creation(self):
        well = SymbolicGravityWell.objects.create(
            source_memory=self.memory,
            influence_radius=5.0,
            distortion_effects={},
        )
        self.assertTrue(well.active)
        self.assertEqual(well.source_memory, self.memory)

    def test_memory_harmonics_pulse_creation(self):
        pulse = MemoryHarmonicsPulse.objects.create(
            pulse_id="p1",
            phase_coherence_level=0.9,
            symbolic_tuning_notes="n",
        )
        pulse.linked_assistants.add(self.assistant)
        pulse.applied_to_memory.add(self.memory)
        self.assertEqual(pulse.linked_assistants.count(), 1)
        self.assertEqual(pulse.applied_to_memory.count(), 1)
