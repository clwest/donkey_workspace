import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, TokenUsage, ChatSession


class DelegationTokenTest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="delegate", password="pw")
        self.client.force_authenticate(self.user)
        self.assistant = Assistant.objects.create(name="Helper", specialty="test")
        self.url = f"/api/assistants/{self.assistant.slug}/chat/"

    def _make_completion(self, prompt, completion):
        class Usage:
            def __init__(self, p, c):
                self.prompt_tokens = p
                self.completion_tokens = c
                self.total_tokens = p + c

        class Msg:
            content = "Hi"

        class Choice:
            message = Msg()

        class Completion:
            def __init__(self):
                self.choices = [Choice()]
                self.usage = Usage(prompt, completion)

        return Completion()

    @patch("assistants.views.assistants.spawn_delegated_assistant")
    @patch("assistants.views.assistants.client.chat.completions.create")
    def test_delegation_triggered(self, mock_create, mock_spawn):
        session_id = str(uuid.uuid4())
        mock_create.return_value = self._make_completion(30, 25)
        mock_spawn.return_value = type("A", (), {"slug": "child"})()
        self.assistant.delegation_threshold_tokens = 50
        self.assistant.save()
        payload = {"message": "hello", "session_id": session_id}
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, 200)
        mock_spawn.assert_called_once()
        self.assertEqual(resp.data.get("delegate_slug"), "child")
        usage = TokenUsage.objects.get(session__session_id=session_id)
        self.assertEqual(usage.total_tokens, 55)

    @patch("assistants.views.assistants.spawn_delegated_assistant")
    @patch("assistants.views.assistants.client.chat.completions.create")
    def test_delegation_not_triggered_below_limit(self, mock_create, mock_spawn):
        session_id = str(uuid.uuid4())
        mock_create.return_value = self._make_completion(20, 20)
        self.assistant.delegation_threshold_tokens = 200
        self.assistant.save()
        payload = {"message": "hi", "session_id": session_id}
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, 200)
        mock_spawn.assert_not_called()
        usage = TokenUsage.objects.get(session__session_id=session_id)
        self.assertEqual(usage.total_tokens, 40)

    @patch("assistants.views.assistants.spawn_delegated_assistant")
    @patch("assistants.views.assistants.client.chat.completions.create")
    def test_existing_usage_triggers_delegation_before_completion(
        self, mock_create, mock_spawn
    ):
        session_id = str(uuid.uuid4())
        self.assistant.delegation_threshold_tokens = 10
        self.assistant.save()
        chat_session = ChatSession.objects.create(
            assistant=self.assistant, session_id=session_id
        )
        TokenUsage.objects.create(
            session=chat_session,
            assistant=self.assistant,
            user=self.user,
            usage_type="chat",
            total_tokens=15,
        )
        payload = {"message": "hey", "session_id": session_id}
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, 200)
        mock_spawn.assert_called_once()
        mock_create.assert_not_called()
