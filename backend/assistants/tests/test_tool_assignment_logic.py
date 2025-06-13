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


class ToolAssignmentLogicTest(TestCase):
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

    def test_assignment_created(self):
        assign = AssistantToolAssignment.objects.create(
            assistant=self.assistant,
            tool=self.tool,
            reason="unit",
            confidence_score=0.8,
        )
        self.assertEqual(assign.tool, self.tool)
        self.assertEqual(assign.assistant, self.assistant)
