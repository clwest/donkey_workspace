import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

import uuid
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant
from tools.models import Tool


class ToolFallbackDelegationTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tool", password="pw")
        self.client.force_authenticate(self.user)
        self.assistant = Assistant.objects.create(name="Helper", specialty="test")
        Tool.objects.create(name="Echo", slug="echo")
        self.url = f"/api/assistants/{self.assistant.slug}/chat/"

    @patch("assistants.views.assistants.spawn_delegated_assistant")
    @patch("assistants.views.assistants.reflect_on_tool_output")
    @patch("assistants.views.assistants.call_tool")
    def test_delegate_when_tool_unsatisfactory(self, mock_call, mock_reflect, mock_spawn):
        mock_call.return_value = {"res": "bad"}
        mock_reflect.return_value = {"summary": "nope", "useful": False, "retry_input": None}
        mock_spawn.return_value = type("A", (), {"slug": "child"})()
        resp = self.client.post(
            self.url,
            {"message": "hi", "session_id": str(uuid.uuid4()), "tool_slug": "echo", "tool_input": {"t": "x"}},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        mock_spawn.assert_called_once()
        self.assertEqual(resp.data["delegate_slug"], "child")

    @patch("assistants.views.assistants.spawn_delegated_assistant")
    @patch("assistants.views.assistants.reflect_on_tool_output")
    @patch("assistants.views.assistants.call_tool")
    def test_retry_with_modified_input(self, mock_call, mock_reflect, mock_spawn):
        mock_call.side_effect = [{"res": "bad"}, {"res": "good"}]
        mock_reflect.return_value = {"summary": "fix", "useful": False, "retry_input": {"t": "y"}}
        resp = self.client.post(
            self.url,
            {"message": "go", "session_id": str(uuid.uuid4()), "tool_slug": "echo", "tool_input": {"t": "x"}},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(mock_call.call_count, 2)
        mock_spawn.assert_not_called()
