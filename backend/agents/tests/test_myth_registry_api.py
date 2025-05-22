import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from assistants.models import Assistant, AssistantGuild, AssistantCivilization
from story.models import LoreEntry
from agents.models import SwarmMemoryEntry, LoreToken
from embeddings.models import EMBEDDING_LENGTH


class MythRegistryAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="api", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="logic")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.token = LoreToken.objects.create(
            name="t",
            summary="s",
            symbolic_tags={},
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=self.assistant,
        )
        lore = LoreEntry.objects.create(title="Root", content="x")
        guild = AssistantGuild.objects.create(name="G", founding_myth=lore)
        self.civ = AssistantCivilization.objects.create(
            name="Civ", myth_root=lore, symbolic_domain="dream"
        )
        self.civ.founding_guilds.add(guild)

    def test_create_registry_and_compliance(self):
        reg_resp = self.client.post(
            "/api/v1/agents/myth-registry/",
            {
                "memory": self.memory.id,
                "registered_by": self.assistant.id,
                "signature": "sig",
                "verified_token": self.token.id,
            },
        )
        self.assertEqual(reg_resp.status_code, 201)

        anchor_resp = self.client.post(
            "/api/v1/agents/lore-anchors/",
            {
                "anchor_type": "equinox",
                "timestamp": timezone.now().isoformat(),
                "attached_tokens": [self.token.id],
                "coordinating_civilizations": [self.civ.id],
                "narrative_impact_summary": "impact",
            },
        )
        self.assertEqual(anchor_resp.status_code, 201)
        anchor_id = anchor_resp.json()["id"]

        comp_resp = self.client.post(
            "/api/v1/agents/ritual-compliance/",
            {
                "civilization": self.civ.id,
                "anchor": anchor_id,
                "compliance_status": "fulfilled",
            },
        )
        self.assertEqual(comp_resp.status_code, 201)

        list_resp = self.client.get("/api/v1/agents/myth-registry/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.json()), 1)
