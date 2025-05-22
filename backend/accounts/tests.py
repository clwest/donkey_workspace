import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import UserMemory, UserPrompts, UserInteractionSummary


class AccountsModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_custom_user_created(self):
        self.assertTrue(self.user.pk)
        # Personal assistant created via signal
        self.assertIsNotNone(self.user.personal_assistant)

    def test_user_memory_creation(self):
        mem = UserMemory.objects.create(
            user=self.user, memory_key="foo", memory_value={"bar": 1}
        )
        self.assertEqual(mem.user, self.user)
        self.assertEqual(mem.memory_key, "foo")

    def test_user_prompt_creation(self):
        prompt = UserPrompts.objects.create(
            user=self.user, prompt_key="greet", prompt_text="hello"
        )
        self.assertEqual(prompt.user, self.user)
        self.assertEqual(prompt.prompt_key, "greet")

    def test_interaction_summary_creation(self):
        summary = UserInteractionSummary.objects.create(
            user=self.user,
            period_start=timezone.now(),
            period_end=timezone.now(),
            message_count=1,
            average_sentiment=0.5,
        )
        self.assertEqual(summary.user, self.user)
        self.assertEqual(summary.message_count, 1)
