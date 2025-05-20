import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase

from tools.models import Tool, ToolUsageLog
from tools.utils.tool_registry import register_tool, call_tool


class ToolRegistryTest(TestCase):
    def test_register_and_call(self):
        def echo(data):
            return {"echo": data["text"]}

        register_tool("Echo", "echo", {}, echo)
        self.assertTrue(Tool.objects.filter(slug="echo").exists())

        result = call_tool("echo", {"text": "hi"}, None)
        self.assertEqual(result, {"echo": "hi"})
        log = ToolUsageLog.objects.get()
        self.assertEqual(log.status, "success")
        self.assertEqual(log.input_data["text"], "hi")

    def test_error_logging(self):
        def fails(data):
            raise ValueError("fail")

        register_tool("Fail", "fail", {}, fails)
        result = call_tool("fail", {}, None)
        log = ToolUsageLog.objects.filter(tool__slug="fail").first()
        self.assertEqual(log.status, "error")
        self.assertIn("fail", log.output_data["error"])
        self.assertIn("error", result)
