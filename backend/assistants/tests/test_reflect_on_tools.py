# flake8: noqa
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402

django.setup()

from django.test import TestCase  # noqa: E402
from assistants.models import Assistant  # noqa: E402
from assistants.models.tooling import (
    AssistantTool,
    AssistantToolAssignment,
)  # noqa: E402
from assistants.utils.assistant_reflection_engine import (
    reflect_on_tools,
)  # noqa: E402


class ReflectOnToolsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(
            name="A",
            specialty="testing",
        )
        self.tool = AssistantTool.objects.create(
            assistant=self.assistant,
            name="Tester",
            slug="tester",
        )
        AssistantToolAssignment.objects.create(
            assistant=self.assistant,
            tool=self.tool,
            reason="auto",
            confidence_score=0.5,
        )

    def test_reflection_summary(self):
        log = reflect_on_tools(self.assistant)
        self.assertIn("Tester", log.summary)
