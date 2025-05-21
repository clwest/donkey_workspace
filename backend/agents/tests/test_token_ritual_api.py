import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, LoreToken
from embeddings.models import EMBEDDING_LENGTH
from unittest.mock import patch


class TokenRitualAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="x")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    @patch("agents.utils.lore_token.get_embedding_for_text")
    @patch("agents.utils.lore_token.call_llm")
    def test_ritual_pipeline(self, mock_call, mock_embed):
        mock_call.return_value = "s"
        mock_embed.return_value = [0.1] * EMBEDDING_LENGTH
        resp = self.client.post(
            "/api/agents/token-rituals/",
            {
                "initiating_assistant": self.assistant.id,
                "base_memory_ids": [self.memory.id],
                "symbolic_intent": "share",
                "token_type": "echo",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        ritual_id = resp.json()["id"]
        resp = self.client.post(
            "/api/agents/token-rituals/",
            {"ritual": ritual_id, "complete": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(LoreToken.objects.count(), 1)

    @patch("agents.utils.lore_token.get_embedding_for_text")
    @patch("agents.utils.lore_token.call_llm")
    def test_token_type_filter(self, mock_call, mock_embed):
        mock_call.return_value = "s"
        mock_embed.return_value = [0.0] * EMBEDDING_LENGTH
        t1 = LoreToken.objects.create(
            name="a",
            summary="b",
            symbolic_tags={},
            token_type="insight",
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=self.assistant,
        )
        t2 = LoreToken.objects.create(
            name="c",
            summary="d",
            symbolic_tags={},
            token_type="echo",
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=self.assistant,
        )
        resp = self.client.get("/api/agents/lore-tokens/?token_type=echo")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], str(t2.id))
