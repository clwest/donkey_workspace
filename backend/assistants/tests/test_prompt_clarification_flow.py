import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, AssistantThoughtLog
from prompts.models import Prompt, PromptMutationLog


class PromptClarificationFlowTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="clar", password="pw")
        self.client.force_authenticate(user=self.user)
        self.prompt = Prompt.objects.create(title="Base", content="Do it", source="test")
        self.assistant = Assistant.objects.create(name="A", specialty="s", system_prompt=self.prompt)

    def test_clarify_prompt_endpoint(self):
        url = f"/api/assistants/{self.assistant.slug}/clarify_prompt/"
        resp = self.client.post(url, {"text": "unhelpful"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(PromptMutationLog.objects.filter(original_prompt=self.prompt).exists())
        self.assertTrue(AssistantThoughtLog.objects.filter(thought_type="prompt_clarification").exists())
