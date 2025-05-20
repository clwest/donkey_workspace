import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model

from assistants.models import Assistant
from tools.models import ToolScore
from tools.utils.tool_registry import (
    register_tool,
    call_tool,
    get_best_tool_for_context,
)


class ToolScoreTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="ts", password="pw")
        self.assistant = Assistant.objects.create(
            name="Tooly", specialty="scoring", created_by=self.user
        )

        def succeed(data):
            return {"ok": True}

        def fail(data):
            raise ValueError("bad")

        register_tool("Good", "good_tool", {}, succeed)
        register_tool("Bad", "bad_tool", {}, fail)

    def test_score_updates(self):
        call_tool("good_tool", {}, self.assistant, tags=["alpha"])
        score = ToolScore.objects.get(tool__slug="good_tool", assistant=self.assistant)
        self.assertEqual(score.usage_count, 1)
        self.assertEqual(score.score, 1.0)
        self.assertIn("alpha", score.context_tags)

    def test_best_tool_selection(self):
        call_tool("good_tool", {}, self.assistant, tags=["alpha"])
        call_tool("bad_tool", {}, self.assistant, tags=["alpha"])
        best = get_best_tool_for_context(["alpha"], self.assistant)
        self.assertIsNotNone(best)
        self.assertEqual(best.slug, "good_tool")
