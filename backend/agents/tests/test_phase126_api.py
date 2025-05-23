import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    EncodedRitualBlueprint,
)


class Phase126APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.blueprint = EncodedRitualBlueprint.objects.create(
            name="R", encoded_steps=[]
        )

    def test_create_myth_record(self):
        resp = self.client.post(
            "/api/myth/record/",
            {
                "recorder_id": "u1",
                "linked_assistant": self.assistant.id,
                "memory_reference": [self.memory.id],
                "symbolic_tags": {},
                "story_notes": "n",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/myth/record/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_symbolic_doc(self):
        resp = self.client.post(
            "/api/docs/symbolic/",
            {
                "author_id": "u1",
                "codex_reference": self.codex.id,
                "entry_title": "T",
                "symbolic_themes": {},
                "ritual_connection": self.blueprint.id,
                "content_body": "b",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/docs/symbolic/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_belief_artifact(self):
        resp = self.client.post(
            "/api/artifacts/archive/",
            {
                "contributor_id": "u1",
                "artifact_type": "scroll",
                "artifact_title": "A",
                "symbolic_payload": {},
                "related_codices": [self.codex.id],
                "archived_memory": [self.memory.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/artifacts/archive/")
        self.assertEqual(len(list_resp.json()), 1)
