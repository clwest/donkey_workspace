import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from tools.models import Tool, ToolExecutionLog

class ToolDetailAPITest(APITestCase):
    def setUp(self):
        self.tool = Tool.objects.create(name="Echo", slug="echo", module_path="x", function_name="f")

    def test_detail_endpoint(self):
        url = f"/api/tools/{self.tool.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], self.tool.id)

    def test_logs_endpoint(self):
        ToolExecutionLog.objects.create(tool=self.tool, input_data={}, success=True)
        url = f"/api/tools/{self.tool.id}/logs/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
