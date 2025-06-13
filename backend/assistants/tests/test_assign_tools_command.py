# flake8: noqa
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402

django.setup()

from django.core.management import call_command  # noqa: E402
from django.test import TestCase  # noqa: E402
from assistants.models import Assistant  # noqa: E402
from assistants.models.tooling import (
    AssistantTool,
    AssistantToolAssignment,
)  # noqa: E402


class AssignToolsCommandTest(TestCase):
    def test_command(self):
        a = Assistant.objects.create(name="A", specialty="t")
        AssistantTool.objects.create(assistant=a, name="T", slug="t")
        call_command("assign_tools_to_assistants")
        exists = AssistantToolAssignment.objects.filter(
            assistant=a, tool__slug="t"
        ).exists()
        self.assertTrue(exists)
