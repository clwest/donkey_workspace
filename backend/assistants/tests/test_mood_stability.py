
from django.test import TestCase
from django.contrib.auth import get_user_model

from assistants.models import Assistant
from assistants.helpers.logging_helper import log_assistant_thought
from assistants.helpers.mood import is_in_cooldown


class MoodStabilityIndexTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="mooder", password="pw")
        self.assistant = Assistant.objects.create(
            name="MoodBot", specialty="x", created_by=self.user
        )

    def test_index_drops_on_mood_swings(self):
        log_assistant_thought(self.assistant, "I am optimistic about our progress.")
        initial = Assistant.objects.get(id=self.assistant.id).mood_stability_index
        log_assistant_thought(self.assistant, "I'm suddenly anxious about failure")
        self.assistant.refresh_from_db()
        self.assertLess(self.assistant.mood_stability_index, initial)
        self.assertIsNotNone(self.assistant.last_mood_shift)

    def test_cooldown_trigger(self):
        self.assistant.mood_stability_index = 0.4
        self.assistant.save()
        self.assertTrue(is_in_cooldown(self.assistant))
