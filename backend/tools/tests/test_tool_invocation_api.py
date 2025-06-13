import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from rest_framework import status

from tools.models import Tool, ToolExecutionLog


def echo_tool(text):
    return {"echo": text}


class ToolInvocationAPITest(APITestCase):
    def setUp(self):
        self.tool = Tool.objects.create(
            slug="echo",
            name="Echo",
            module_path="tools.tests.test_tool_invocation_api",
            function_name="echo_tool",
        )

    def test_invoke_tool(self):
        url = f"/api/tools/{self.tool.id}/execute/"
        resp = self.client.post(url, {"text": "hi"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["result"], {"echo": "hi"})
        self.assertEqual(ToolExecutionLog.objects.count(), 1)
        usage = ToolExecutionLog.objects.first()
        self.assertTrue(usage.success)
        self.assertEqual(usage.tool, self.tool)
