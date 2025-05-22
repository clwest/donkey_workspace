
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from unittest.mock import patch

from assistants.models import Assistant
from intel_core.models import Document
from prompts.models import Prompt


class KnowledgeDiffAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="diff", password="pw")
        self.client.force_authenticate(user=self.user)
        self.prompt = Prompt.objects.create(title="Base", content="Be helpful", source="test")
        self.assistant = Assistant.objects.create(name="KD", specialty="donkeys", system_prompt=self.prompt)
        self.doc = Document.objects.create(title="Donkey Guide", content="All about donkeys", source_type="text")

    @patch("assistants.views.knowledge.client.chat.completions.create")
    def test_diff_knowledge_with_doc(self, mock_create):
        class Msg:
            content = '{"diff_summary": "ok", "prompt_updates": "add info", "tone_suggestions": "cheerful"}'
        class Choice:
            message = Msg()
        class Completion:
            def __init__(self):
                self.choices = [Choice()]
        mock_create.return_value = Completion()

        url = f"/api/v1/assistants/{self.assistant.slug}/diff-knowledge/"
        resp = self.client.post(url, {"document_id": str(self.doc.id)}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("diff_summary", data)
        self.assertIn("prompt_updates", data)

    def test_diff_knowledge_requires_input(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/diff-knowledge/"
        resp = self.client.post(url, {}, format="json")
        self.assertEqual(resp.status_code, 400)

