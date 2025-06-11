import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from unittest.mock import patch
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import MemoryEntry
from mcp_core.models import Tag


class ChatIdentityRouteTest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(
            name="Demo", slug="demo", is_demo=True
        )

    @patch("assistants.views.assistants.client.embeddings.create")
    @patch("assistants.views.assistants.generate_tags_for_memory")
    @patch("utils.llm_router.chat")
    def test_chat_generates_tags(self, mock_chat, mock_tags, mock_embed):
        mock_chat.return_value = ("ok", [], {})
        tag = Tag.objects.create(slug="greet", name="greet")
        mock_tags.return_value = ["greet"]
        mock_embed.return_value = type(
            "E", (), {"data": [type("D", (), {"embedding": []})]}
        )()
        resp = self.client.post(
            f"/api/assistants/{self.assistant.slug}/chat/",
            {"message": "hi", "session_id": "s1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        mem = MemoryEntry.objects.filter(assistant=self.assistant).last()
        self.assertIn(tag, mem.tags.all())

    def test_identity_route_demo(self):
        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/identity/")
        self.assertEqual(resp.status_code, 200)

    def test_identity_route_demo_any_user(self):
        owner = self.user
        self.assistant.created_by = owner
        self.assistant.save()
        self.authenticate("viewer")
        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/identity/")
        self.assertEqual(resp.status_code, 200)

    def test_identity_route_non_demo(self):
        self.assistant.is_demo = False
        self.assistant.created_by = self.user
        self.assistant.save()
        self.client.logout()
        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/identity/")
        self.assertEqual(resp.status_code, 200)
