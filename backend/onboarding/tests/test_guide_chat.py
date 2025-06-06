import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch

class GuideChatAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="guide", password="pw")
        self.client.force_authenticate(user=self.user)
        from assistants.models import Assistant
        self.assistant = Assistant.objects.create(
            name="GuideA", slug="guide-a", created_by=self.user
        )

    @patch("onboarding.utils.complete_chat")
    def test_chat_reply(self, mock_chat):
        mock_chat.return_value = "Hello!"
        resp = self.client.post("/api/onboarding/guide_chat/", {"message": "hi"}, format="json")
        assert resp.status_code == 200
        assert resp.json()["reply"] == "Hello!"

    @patch("onboarding.utils.complete_chat")
    def test_hint_suggestion(self, mock_chat):
        mock_chat.return_value = "Hi"
        resp = self.client.post(
            "/api/onboarding/guide_chat/",
            {"message": "hi"},
            format="json",
        )
        data = resp.json()
        assert resp.status_code == 200
        assert data["hint_suggestion"] == "glossary_tour"
        assert data["ui_action"].startswith("goto:")

    def test_dismiss(self):
        resp = self.client.post("/api/onboarding/guide_chat/", {"dismiss": True}, format="json")
        assert resp.status_code == 200
        self.user.refresh_from_db()
        assert self.user.dismissed_guide is True
