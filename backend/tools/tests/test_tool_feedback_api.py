import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from assistants.models import Assistant
from prompts.models import Prompt
from tools.models import Tool, ToolUsageLog


class ToolFeedbackAPITest(APITestCase):
    def setUp(self):
        self.prompt = Prompt.objects.create(title="P", content="Do it", source="t")
        self.assistant = Assistant.objects.create(name="A", specialty="s", system_prompt=self.prompt)
        self.tool = Tool.objects.create(name="Echo", slug="echo", module_path="x", function_name="f")
        self.log = ToolUsageLog.objects.create(tool=self.tool, assistant=self.assistant, input_payload={})

    def test_submit_feedback_triggers_mutation(self):
        url = f"/api/tools/feedback/{self.log.id}/"
        resp = self.client.post(url, {"feedback": "not_helpful", "message": "bad"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.log.refresh_from_db()
        self.assertEqual(self.log.feedback, "not_helpful")
        self.assistant.refresh_from_db()
        self.assertNotEqual(self.assistant.system_prompt, self.prompt)
        self.assertTrue(ToolUsageLog.objects.filter(id=self.log.id, feedback="not_helpful").exists())
