import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmCodex, SwarmMemoryEntry


class Phase139APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(title="C", created_by=self.assistant, symbolic_domain="myth")

    def test_create_reflection_chamber(self):
        resp = self.client.post(
            "/api/reflection/chamber/",
            {
                "chamber_title": "Ch",
                "participant_ids": [self.assistant.id],
                "codex_review": self.codex.id,
                "memory_archive": [self.memory.id],
                "ritual_scorecards": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/reflection/chamber/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_dialogue_amplifier(self):
        resp = self.client.post(
            "/api/dialogue/amplify/",
            {
                "amplifier_title": "Amp",
                "agents_involved": [self.assistant.id],
                "active_codex": self.codex.id,
                "layered_response": "r",
                "symbolic_resonance_score": 0.5,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/dialogue/amplify/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_resolution_sequence(self):
        resp = self.client.post(
            "/api/sequence/resolve/",
            {
                "assistant": self.assistant.id,
                "resolution_steps": [{"step": 1}],
                "codex_closure_state": "end",
                "legacy_artifacts": {},
                "symbolic_final_score": 1.0,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/sequence/resolve/")
        self.assertEqual(len(list_resp.json()), 1)
