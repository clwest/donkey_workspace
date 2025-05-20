import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch
from assistants.models import Assistant, AssistantThoughtLog
from tools.utils.tool_reflection import reflect_on_tool_output


class ToolReflectionTest(TestCase):
    @patch("tools.utils.tool_reflection.client.chat.completions.create")
    def test_reflection_parsed_and_logged(self, mock_create):
        class Msg:
            content = '{"summary": "bad", "useful": false, "retry_input": {"q": "new"}}'

        class Choice:
            message = Msg()

        mock_create.return_value = type("C", (), {"choices": [Choice()]})()
        assistant = Assistant.objects.create(name="A", specialty="t")
        result = reflect_on_tool_output({"ok": True}, "echo", {"q": "hi"}, assistant)
        self.assertEqual(result["summary"], "bad")
        self.assertFalse(result["useful"])
        self.assertEqual(result["retry_input"], {"q": "new"})
        log = AssistantThoughtLog.objects.filter(event="tool_reflection").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.thought, "bad")
