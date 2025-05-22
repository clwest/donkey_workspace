import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import BeliefBiome


class Phase60APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.biome = BeliefBiome.objects.create(name="B", core_traits={}, environmental_factors={})

    def test_create_forecast_pulse(self):
        resp = self.client.post(
            "/api/v1/agents/mythic-forecast/",
            {
                "initiated_by": self.assistant.id,
                "narrative_conditions": "c",
                "forecast_tags": {},
                "pulse_range": "guild",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/mythic-forecast/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_belief_atlas(self):
        resp = self.client.post(
            "/api/v1/agents/belief-atlases/",
            {
                "epoch": "E",
                "scope": "swarm",
                "symbolic_coordinates": {},
                "alignment_map": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/belief-atlases/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_symbolic_weather(self):
        resp = self.client.post(
            "/api/v1/agents/symbolic-weather/",
            {
                "name": "Front",
                "pressure_triggers": {},
                "forecast_duration": 3,
                "projected_effects": "x",
                "affecting_biomes": [self.biome.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/symbolic-weather/")
        self.assertEqual(len(list_resp.json()), 1)
