import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import TranscendentMyth, BeliefBiome, SwarmMemoryEntry
from assistants.models import PurposeRouteMap, AutonomyNarrativeModel


class Phase497ModelTest(TestCase):
    def setUp(self):
        self.a1 = Assistant.objects.create(name="A1")
        self.a2 = Assistant.objects.create(name="A2")
        self.myth = TranscendentMyth.objects.create(name="M")
        self.mem = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_belief_biome(self):
        biome = BeliefBiome.objects.create(name="B", core_traits={"x": 1}, environmental_factors={})
        biome.dominant_myths.add(self.myth)
        biome.member_assistants.add(self.a1, self.a2)
        self.assertEqual(biome.member_assistants.count(), 2)
        self.assertEqual(biome.dominant_myths.count(), 1)

    def test_purpose_route_map(self):
        route = PurposeRouteMap.objects.create(
            assistant=self.a1,
            input_tags={"mood": "happy"},
            output_path="reflect",
            reason="r",
        )
        self.assertEqual(route.assistant, self.a1)

    def test_autonomy_narrative_model(self):
        model = AutonomyNarrativeModel.objects.create(
            assistant=self.a1,
            current_arc="init",
            active_purpose_statement="seek",
            transformation_triggers={},
        )
        model.known_story_events.add(self.mem)
        self.assertEqual(model.known_story_events.count(), 1)
