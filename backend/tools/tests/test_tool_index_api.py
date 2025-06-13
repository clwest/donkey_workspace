import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from assistants.models import Assistant
from assistants.models.tooling import AssistantTool, AssistantToolAssignment
from tools.models import Tool, ToolExecutionLog, ToolReflectionLog


class ToolIndexAPITest(APITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", specialty="t", slug="a")
        self.tool = Tool.objects.create(
            name="T", slug="t", module_path="m", function_name="f"
        )
        at = AssistantTool.objects.create(assistant=self.assistant, name="T", slug="t")
        AssistantToolAssignment.objects.create(
            assistant=self.assistant, tool=at, reason="auto"
        )
        ToolExecutionLog.objects.create(
            tool=self.tool, assistant=self.assistant, input_data={}, success=True
        )
        ToolReflectionLog.objects.create(
            tool=self.tool, assistant=self.assistant, reflection="ok"
        )

    def test_tool_index(self):
        resp = self.client.get("/api/tools/index/")
        self.assertEqual(resp.status_code, 200)
        slugs = [t["slug"] for t in resp.json().get("results", [])]
        self.assertIn("t", slugs)
