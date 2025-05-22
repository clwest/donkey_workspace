import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import TranscendentMyth, SwarmMemoryEntry


class Phase497APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.myth = TranscendentMyth.objects.create(name="M")
        self.memory = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_create_biome(self):
        resp = self.client.post(
            "/api/v1/agents/biomes/",
            {
                "name": "B",
                "core_traits": {"x": 1},
                "environmental_factors": {},
                "dominant_myths": [self.myth.id],
                "member_assistants": [self.assistant.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/biomes/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_purpose_route_and_autonomy_model(self):
        route_resp = self.client.post(
            "/api/v1/assistants/purpose-routing/",
            {
                "assistant": self.assistant.id,
                "input_tags": {"tone": "stern"},
                "output_path": "task",
                "reason": "test",
            },
            format="json",
        )
        self.assertEqual(route_resp.status_code, 201)

        model_resp = self.client.post(
            "/api/v1/assistants/autonomy-models/",
            {
                "assistant": self.assistant.id,
                "current_arc": "init",
                "known_story_events": [self.memory.id],
                "active_purpose_statement": "seek",
                "transformation_triggers": {},
            },
            format="json",
        )
        self.assertEqual(model_resp.status_code, 201)
