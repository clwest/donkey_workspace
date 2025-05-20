import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from assistants.helpers.logging_helper import log_assistant_thought


class ThoughtMoodDetectionTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="p")
        self.assistant = Assistant.objects.create(name="A", specialty="s", created_by=self.user)

    def test_mood_detected(self):
        log = log_assistant_thought(self.assistant, "I am worried about the deadline")
        self.assertEqual(log.mood, "anxious")
