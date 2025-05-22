import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    BeliefBiome,
    MythicForecastPulse,
    BeliefAtlasSnapshot,
    SymbolicWeatherFront,
)


class Phase60ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.biome = BeliefBiome.objects.create(name="B", core_traits={}, environmental_factors={})

    def test_mythic_forecast_pulse(self):
        pulse = MythicForecastPulse.objects.create(
            initiated_by=self.assistant,
            narrative_conditions="c",
            forecast_tags={},
            pulse_range="global",
        )
        self.assertEqual(pulse.initiated_by, self.assistant)
        self.assertEqual(pulse.pulse_range, "global")

    def test_belief_atlas_snapshot(self):
        atlas = BeliefAtlasSnapshot.objects.create(
            epoch="E1",
            scope="swarm",
            symbolic_coordinates={str(self.assistant.id): [0.1, 0.2]},
            alignment_map={},
        )
        self.assertEqual(atlas.scope, "swarm")

    def test_symbolic_weather_front(self):
        front = SymbolicWeatherFront.objects.create(
            name="Storm",
            pressure_triggers={},
            forecast_duration=3,
            projected_effects="chaos",
        )
        front.affecting_biomes.add(self.biome)
        self.assertEqual(front.affecting_biomes.count(), 1)
