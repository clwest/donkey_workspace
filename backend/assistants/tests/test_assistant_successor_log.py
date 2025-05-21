import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, AssistantProject, AssistantSuccessorLog


class AssistantSuccessorLogTest(TestCase):
    def setUp(self):
        self.pre = Assistant.objects.create(name="Pre", specialty="s")
        self.succ = Assistant.objects.create(name="Succ", specialty="s")
        self.project = AssistantProject.objects.create(assistant=self.pre, title="P1")

    def test_create_log(self):
        log = AssistantSuccessorLog.objects.create(
            predecessor=self.pre,
            successor=self.succ,
            reason="retired",
            memory_snapshot="{}",
        )
        log.transferred_projects.add(self.project)
        self.assertEqual(log.predecessor, self.pre)
        self.assertIn(self.project, log.transferred_projects.all())
