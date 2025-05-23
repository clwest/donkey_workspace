import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant, CodexLinkedGuild
from agents.models import SwarmMemoryEntry, SwarmCodex

class Phase1309APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(title="C", created_by=self.assistant, symbolic_domain="myth")
        self.guild = CodexLinkedGuild.objects.create(guild_name="g", codex=self.codex)

    def test_create_mythchain_output(self):
        resp = self.client.post(
            "/api/export/mythchain/",
            {
                "assistant": self.assistant.id,
                "seed_memory": [self.memory.id],
                "output_title": "O",
                "codex_alignment_map": {},
                "symbolic_summary": "s",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/export/mythchain/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_artifact_export(self):
        resp = self.client.post(
            "/api/export/artifact/",
            {
                "assistant": self.assistant.id,
                "artifact_title": "A",
                "export_format": "json",
                "auto_compress": False,
                "symbolic_footer": "f",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/export/artifact/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_broadcast_pattern(self):
        resp = self.client.post(
            "/api/broadcast/patterns/",
            {
                "broadcast_title": "B",
                "source_guild": self.guild.id,
                "symbolic_payload": {},
                "belief_waveform_data": {},
                "target_assistants": [self.assistant.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/broadcast/patterns/")
        self.assertEqual(len(list_resp.json()), 1)
