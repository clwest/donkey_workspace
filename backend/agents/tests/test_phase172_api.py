import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    CodexLinkedGuild,
)


class Phase172APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.guild = CodexLinkedGuild.objects.create(
            guild_name="G",
            anchor_codex=self.codex,
            member_users={},
            ritual_focus={},
            codex_compliance_score=0.9,
        )
        self.guild.member_assistants.add(self.assistant)

    def test_federation_law_treaty_flow(self):
        f_resp = self.client.post(
            "/api/agents/federation/codices/",
            {
                "federation_name": "F",
                "founding_codices": [self.codex.id],
                "governance_rules": {},
                "assistant_moderators": [self.assistant.id],
                "federation_mandates": "m",
            },
            format="json",
        )
        self.assertEqual(f_resp.status_code, 201)
        federation_id = f_resp.json()["id"]

        l_resp = self.client.post(
            "/api/agents/law/ritual/",
            {
                "federation": federation_id,
                "ritual_law_map": {},
                "symbolic_penalties": {},
                "codex_enforcement_routes": "r",
                "assistant_role_enactors": [self.assistant.id],
            },
            format="json",
        )
        self.assertEqual(l_resp.status_code, 201)

        t_resp = self.client.post(
            "/api/agents/treaty/forge/",
            {
                "treaty_title": "T",
                "participating_guilds": [self.guild.id],
                "codex_shared_clauses": {},
                "ritual_bond_requirements": {},
                "symbolic_enforcement_terms": "e",
                "treaty_status": "draft",
            },
            format="json",
        )
        self.assertEqual(t_resp.status_code, 201)

        list_resp = self.client.get("/api/agents/treaty/forge/")
        self.assertEqual(len(list_resp.json()), 1)

