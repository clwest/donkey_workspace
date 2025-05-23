import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant
from agents.models import SwarmCodex, CodexLinkedGuild


class Phase1204APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_create_guild_cluster_and_engine(self):
        g_resp = self.client.post(
            "/api/guilds/",
            {
                "guild_name": "G",
                "anchor_codex": self.codex.id,
                "member_assistants": [self.assistant.id],
                "member_users": [],
                "ritual_focus": {},
                "codex_compliance_score": 0.8,
            },
            format="json",
        )
        self.assertEqual(g_resp.status_code, 201)
        guild_id = g_resp.json()["id"]

        c_resp = self.client.post(
            "/api/communities/",
            {
                "cluster_name": "C",
                "trait_map": {},
                "collective_memory_tags": [],
                "participant_ids": [],
                "shared_archetype_signature": {},
            },
            format="json",
        )
        self.assertEqual(c_resp.status_code, 201)

        s_resp = self.client.post(
            "/api/swarm/",
            {
                "active_guilds": [guild_id],
                "symbolic_state_map": {},
                "federation_log": "log",
                "ritual_convergence_score": 0.5,
            },
            format="json",
        )
        self.assertEqual(s_resp.status_code, 201)

        list_resp = self.client.get("/api/swarm/")
        self.assertEqual(len(list_resp.json()), 1)
