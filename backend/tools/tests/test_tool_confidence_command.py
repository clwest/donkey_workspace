import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django
django.setup()

from django.test import TestCase
from django.core.management import call_command
from assistants.models import Assistant
from tools.models import Tool, ToolUsageLog, ToolReflectionLog, ToolConfidenceSnapshot


class ToolConfidenceCommandTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", specialty="t")
        self.tool = Tool.objects.create(name="T", slug="t", module_path="m", function_name="f")
        ToolUsageLog.objects.create(tool=self.tool, assistant=self.assistant, input_payload={}, success=True)
        ToolReflectionLog.objects.create(tool=self.tool, assistant=self.assistant, reflection="ok", confidence_score=0.8)

    def test_command_creates_snapshot(self):
        call_command("summarize_tool_confidence")
        snap = ToolConfidenceSnapshot.objects.get(tool=self.tool, assistant=self.assistant)
        self.assertAlmostEqual(snap.confidence_score, 0.8, places=2)
