import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SymbolicAlliance, SwarmMemoryEntry


class Phase499APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="t", content="c")
        self.alliance = SymbolicAlliance.objects.create(
            name="Alliance",
            aligned_beliefs={},
            shared_purpose_vector={},
        )
        self.alliance.founding_assistants.add(self.assistant)

    def test_create_codex(self):
        resp = self.client.post(
            "/api/v1/codexes/",
            {
                "title": "C",
                "created_by": self.assistant.id,
                "symbolic_domain": "knowledge",
                "governing_alliances": [self.alliance.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/codexes/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_symbolic_law(self):
        codex_resp = self.client.post(
            "/api/v1/codexes/",
            {
                "title": "C2",
                "created_by": self.assistant.id,
                "symbolic_domain": "diplomacy",
                "governing_alliances": [self.alliance.id],
            },
            format="json",
        )
        codex_id = codex_resp.json()["id"]
        resp = self.client.post(
            "/api/v1/symbolic-laws/",
            {
                "codex": codex_id,
                "description": "d",
                "symbolic_tags": {},
                "derived_from_memory": self.memory.id,
                "enforcement_scope": "global",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/symbolic-laws/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_ritual_archive(self):
        codex_resp = self.client.post(
            "/api/v1/codexes/",
            {
                "title": "C3",
                "created_by": self.assistant.id,
                "symbolic_domain": "transformation",
                "governing_alliances": [self.alliance.id],
            },
            format="json",
        )
        codex_id = codex_resp.json()["id"]
        resp = self.client.post(
            "/api/v1/ritual-archives/",
            {
                "name": "R",
                "related_memory": self.memory.id,
                "ceremony_type": "init",
                "symbolic_impact_summary": "s",
                "locked_by_codex": codex_id,
                "participant_assistants": [self.assistant.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/ritual-archives/")
        self.assertEqual(len(list_resp.json()), 1)
