
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from unittest.mock import patch
from assistants.models import Assistant, AssistantThoughtLog


class DreamModeAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="dreamer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="DreamBot", specialty="sleep")

    @patch("assistants.utils.assistant_thought_engine.client.chat.completions.create")
    def test_dream_endpoint_logs_dream_mode(self, mock_create):
        class Msg:
            content = "Imagine"  # dummy

        class Choice:
            message = Msg()

        class Completion:
            def __init__(self):
                self.choices = [Choice()]

        mock_create.return_value = Completion()

        url = f"/api/v1/assistants/{self.assistant.slug}/dream/"
        resp = self.client.post(url, {}, format="json")
        self.assertEqual(resp.status_code, 200)
        log = AssistantThoughtLog.objects.filter(assistant=self.assistant).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.mode, "dream")
