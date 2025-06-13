import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from tools.models import Tool, ToolUsageLog, ToolReflectionLog


class ToolConfidenceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="A", specialty="t", slug="a")
        self.tool = Tool.objects.create(name="T", slug="t", module_path="m", function_name="f")
        ToolUsageLog.objects.create(tool=self.tool, assistant=self.assistant, input_payload={}, success=True)
        ToolReflectionLog.objects.create(tool=self.tool, assistant=self.assistant, reflection="ok", confidence_score=0.8)

    def test_list_confidence(self):
        r = self.client.get(f"/api/assistants/{self.assistant.slug}/tools/confidence/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["results"])
