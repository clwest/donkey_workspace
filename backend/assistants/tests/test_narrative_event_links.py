import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant, AssistantThoughtLog, AssistantReflectionLog, AssistantProject
from story.models import NarrativeEvent

class NarrativeEventLinkTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="test", password="pw")
        self.assistant = Assistant.objects.create(name="A", specialty="s", created_by=self.user)
        self.project = AssistantProject.objects.create(assistant=self.assistant, title="P", created_by=self.user)
        self.event = NarrativeEvent.objects.create(title="E1")

    def test_thought_log_links_event(self):
        log = AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="hi",
            linked_event=self.event,
        )
        self.assertEqual(log.linked_event, self.event)

    def test_reflection_links_event(self):
        ref = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            title="R",
            summary="s",
            linked_event=self.event,
        )
        self.assertEqual(ref.linked_event, self.event)

