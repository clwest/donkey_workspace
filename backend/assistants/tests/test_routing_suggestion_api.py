import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch

from assistants.models import Assistant
from embeddings.models import EMBEDDING_LENGTH


class RoutingSuggestionAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="router", password="pw")
        self.client.force_authenticate(self.user)
        self.a1 = Assistant.objects.create(name="Coder", specialty="code")
        self.a2 = Assistant.objects.create(name="Writer", specialty="docs")
        self.a1.capability_embedding = [1.0] * EMBEDDING_LENGTH
        self.a1.save()
        self.a2.capability_embedding = [0.5] * EMBEDDING_LENGTH
        self.a2.save()
        self.url = "/api/assistants/suggest/"

    @patch("assistants.utils.routing_suggestion.get_embedding_for_text")
    def test_returns_best_match(self, mock_emb):
        mock_emb.return_value = [1.0] * EMBEDDING_LENGTH
        resp = self.client.post(
            self.url,
            {
                "context_summary": "fix bug in code",
                "tags": ["code"],
                "recent_messages": [],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["suggested_assistant"]["slug"], self.a1.slug)
        self.assertIn("confidence", data)
