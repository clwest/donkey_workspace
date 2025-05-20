import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine


class ReflectionPromptToneTest(TestCase):
    def test_prompt_contains_tone_questions(self):
        a = Assistant.objects.create(name="R", specialty="s")
        engine = AssistantReflectionEngine(a)
        prompt = engine.build_reflection_prompt(["m1"])
        self.assertIn("Was your tone appropriate", prompt)
        self.assertIn("different emotional state", prompt)
