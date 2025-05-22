import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import BeliefBiome


class Phase498APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.biome = BeliefBiome.objects.create(name="B", core_traits={}, environmental_factors={})

    def test_create_alliance(self):
        resp = self.client.post(
            "/api/agents/alliances/",
            {
                "name": "Al",
                "aligned_beliefs": {},
                "shared_purpose_vector": {},
                "founding_assistants": [self.assistant.id],
                "member_biomes": [self.biome.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/alliances/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_dream_negotiation(self):
        resp = self.client.post(
            "/api/agents/dream-negotiation/",
            {
                "proposed_purpose_update": "p",
                "symbolic_context": {},
                "participants": [self.assistant.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/dream-negotiation/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_biome_mutation(self):
        resp = self.client.post(
            "/api/agents/biome-mutations/",
            {
                "biome": self.biome.id,
                "trigger_type": "belief shift",
                "mutation_summary": "s",
                "new_traits": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/biome-mutations/")
        self.assertEqual(len(list_resp.json()), 1)
