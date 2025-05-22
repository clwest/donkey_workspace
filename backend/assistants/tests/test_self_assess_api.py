
from assistants.tests import BaseAPITestCase
from unittest.mock import patch
from assistants.models import Assistant, AssistantThoughtLog
import json


class SelfAssessAPITest(BaseAPITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Assess", specialty="x")
        self.url = f"/api/v1/assistants/{self.assistant.slug}/self-assess/"

    @patch("assistants.views.assistants.call_llm")
    def test_self_assess_endpoint(self, mock_call):
        mock_call.return_value = json.dumps(
            {
                "score": 0.8,
                "role": "ok",
                "prompt_tweaks": "none",
                "summary": "fine",
            }
        )
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("score", data)
        log = AssistantThoughtLog.objects.filter(
            assistant=self.assistant, thought_type="identity_reflection"
        ).first()
        self.assertIsNotNone(log)
