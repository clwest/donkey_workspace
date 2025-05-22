import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    BeliefBiome,
    SymbolicAlliance,
    DreamPurposeNegotiation,
    BiomeMutationEvent,
)


class Phase498ModelTest(TestCase):
    def setUp(self):
        self.a1 = Assistant.objects.create(name="A1")
        self.a2 = Assistant.objects.create(name="A2")
        self.biome = BeliefBiome.objects.create(name="B", core_traits={}, environmental_factors={})

    def test_symbolic_alliance(self):
        alliance = SymbolicAlliance.objects.create(
            name="Alliance",
            aligned_beliefs={},
            shared_purpose_vector={},
        )
        alliance.founding_assistants.add(self.a1, self.a2)
        alliance.member_biomes.add(self.biome)
        self.assertEqual(alliance.founding_assistants.count(), 2)
        self.assertEqual(alliance.member_biomes.count(), 1)

    def test_dream_purpose_negotiation(self):
        negotiation = DreamPurposeNegotiation.objects.create(
            proposed_purpose_update="x",
            symbolic_context={},
        )
        negotiation.participants.add(self.a1, self.a2)
        self.assertEqual(negotiation.participants.count(), 2)
        self.assertFalse(negotiation.consensus_reached)

    def test_biome_mutation_event(self):
        event = BiomeMutationEvent.objects.create(
            biome=self.biome,
            trigger_type="memory overload",
            mutation_summary="m",
            new_traits={},
        )
        self.assertEqual(event.biome, self.biome)
