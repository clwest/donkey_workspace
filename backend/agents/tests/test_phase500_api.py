import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant, AssistantGuild
from agents.models import SwarmCodex, SwarmMemoryEntry


class Phase500APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.guild = AssistantGuild.objects.create(name="G")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.memory = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_create_polity(self):
        resp = self.client.post(
            "/api/v1/polities/",
            {
                "name": "P",
                "founding_codex": self.codex.id,
                "core_purpose_statement": "p",
                "member_guilds": [self.guild.id],
                "leadership_assistants": [self.assistant.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/polities/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_election(self):
        polity_resp = self.client.post(
            "/api/v1/polities/",
            {
                "name": "P2",
                "founding_codex": self.codex.id,
                "core_purpose_statement": "p",
            },
            format="json",
        )
        polity_id = polity_resp.json()["id"]
        resp = self.client.post(
            "/api/v1/elections/",
            {
                "polity": polity_id,
                "election_type": "rotation",
                "candidates": [self.assistant.id],
                "ballot_memory": self.memory.id,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/elections/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_legacy_role(self):
        resp = self.client.post(
            "/api/v1/legacy-roles/",
            {
                "role_name": "Herald",
                "assigned_to": self.assistant.id,
                "bonded_memory": self.memory.id,
                "renewal_conditions": "yearly",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/legacy-roles/")
        self.assertEqual(len(list_resp.json()), 1)
