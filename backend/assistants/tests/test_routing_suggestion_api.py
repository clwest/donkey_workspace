import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch

from assistants.models import Assistant, RoutingSuggestionLog
from embeddings.models import EMBEDDING_LENGTH

class RoutingSuggestionAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="router", password="pw")
        self.client.force_authenticate(self.user)
        self.assistant = Assistant.objects.create(name="Coder", specialty="code")
        self.assistant.capability_embedding = [1.0] * EMBEDDING_LENGTH
        self.assistant.save()
        self.url = "/api/assistants/suggest/"

    @patch("assistants.utils.delegation_router.get_embedding_for_text")
    def test_logs_suggestion(self, mock_emb):
        mock_emb.return_value = [1.0] * EMBEDDING_LENGTH
        resp = self.client.post(self.url, {"text": "write code"}, format="json")
        self.assertEqual(resp.status_code, 200)
        log = RoutingSuggestionLog.objects.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.suggested_assistant, self.assistant)

    @patch("assistants.utils.delegation_router.get_embedding_for_text")
    def test_accept_flag_sets_selected(self, mock_emb):
        mock_emb.return_value = [1.0] * EMBEDDING_LENGTH
        resp = self.client.post(self.url, {"text": "write code", "accepted": True}, format="json")
        self.assertEqual(resp.status_code, 200)
        log = RoutingSuggestionLog.objects.first()
        self.assertTrue(log.selected)
