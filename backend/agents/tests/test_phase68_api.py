import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry

class Phase68APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u68", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="T", content="c")

    def test_create_ritual_blueprint(self):
        resp = self.client.post(
            "/api/agents/ritual-blueprints/",
            {
                "name": "R",
                "creator": self.assistant.id,
                "symbolic_steps": {},
                "transformation_goal": "g",
                "applicable_roles": ["sage"],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/ritual-blueprints/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_ritual_simulation(self):
        bp = self.client.post(
            "/api/agents/ritual-blueprints/",
            {
                "name": "B",
                "creator": self.assistant.id,
                "symbolic_steps": {},
                "transformation_goal": "g",
                "applicable_roles": [],
            },
            format="json",
        ).json()
        resp = self.client.post(
            "/api/agents/ritual-simulations/",
            {
                "assistant": self.assistant.id,
                "blueprint": bp["id"],
                "outcome_description": "ok",
                "symbolic_success_rate": 0.9,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/ritual-simulations/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_memory_reprogramming(self):
        resp = self.client.post(
            "/api/agents/memory-reprogramming/",
            {
                "target_memory": self.memory.id,
                "initiated_by": self.assistant.id,
                "trigger_condition": "dream",
                "rewrite_directive": "revise",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/memory-reprogramming/")
        self.assertEqual(len(list_resp.json()), 1)
