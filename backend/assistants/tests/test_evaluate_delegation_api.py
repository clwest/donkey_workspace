import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant
from unittest.mock import patch


class EvaluateDelegationAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="eval", password="pw")
        self.client.force_authenticate(self.user)
        self.parent = Assistant.objects.create(
            name="Parent", specialty="summarization", delegation_threshold_tokens=30
        )
        self.other = Assistant.objects.create(name="Owl", specialty="summarization")
        self.url = f"/api/assistants/{self.parent.slug}/evaluate-delegation/"

    def test_token_count_recommends_existing(self):
        resp = self.client.post(self.url, {"token_count": 40})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["should_delegate"])
        self.assertEqual(data["suggested_agent"], self.other.slug)

    @patch("assistants.views.delegations.spawn_delegated_assistant")
    def test_spawn_new_when_no_existing(self, mock_spawn):
        Assistant.objects.filter(id=self.other.id).delete()
        mock_spawn.return_value = type("A", (), {"slug": "new"})()
        resp = self.client.post(self.url, {"token_count": 40})
        self.assertEqual(resp.status_code, 200)
        mock_spawn.assert_called_once()
        data = resp.json()
        self.assertTrue(data["should_delegate"])
        self.assertEqual(data["suggested_agent"], "new")
