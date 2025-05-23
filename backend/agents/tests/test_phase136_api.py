import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant
from agents.models import SwarmCodex


class Phase136APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_create_and_list_plans(self):
        resp = self.client.post(
            "/api/roadmaps/symbolic/",
            {
                "plan_title": "Plan",
                "contributors": ["u1"],
                "archetype_path": ["hero"],
                "ritual_checkpoints": [1],
                "codex_constraints": [self.codex.id],
                "memory_segments": [],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/roadmaps/symbolic/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_and_list_arenas(self):
        resp = self.client.post(
            "/api/arenas/myth-planning/",
            {
                "arena_title": "Arena",
                "participant_ids": ["u1"],
                "myth_proposals": {},
                "symbolic_tension_points": {},
                "codex_focus": [self.codex.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        resp = self.client.get("/api/arenas/myth-planning/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_create_and_list_forecasts(self):
        resp = self.client.post(
            "/api/forecast/codex/",
            {
                "forecast_title": "F",
                "codex_inputs": [self.codex.id],
                "narrative_pressure_map": {},
                "projected_mutation_events": {},
                "convergence_score": 0.2,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        resp = self.client.get("/api/forecast/codex/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
