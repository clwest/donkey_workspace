import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from tools.models import Tool, ToolExecutionLog
from assistants.models import Assistant


def echo_tool(text="hi"):
    return {"echo": text}


class ToolExecutionSlugIdTest(APITestCase):
    def setUp(self):
        self.tool = Tool.objects.create(
            slug="echo",
            name="Echo",
            module_path=__name__,
            function_name="echo_tool",
        )
        self.assistant = Assistant.objects.create(name="A", slug="slugger")

    def test_slug_and_id(self):
        url = f"/api/tools/{self.tool.id}/execute/"
        resp = self.client.post(url, {"assistant_id": self.assistant.slug})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            ToolExecutionLog.objects.first().assistant_id, self.assistant.id
        )
        ToolExecutionLog.objects.all().delete()
        resp = self.client.post(url, {"assistant_id": str(self.assistant.id)})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            ToolExecutionLog.objects.first().assistant_id, self.assistant.id
        )
