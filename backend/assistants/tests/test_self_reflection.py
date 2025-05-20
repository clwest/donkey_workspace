import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.core.management import call_command
from unittest.mock import patch
import uuid
from rest_framework.test import APITestCase

from assistants.models import Assistant, AssistantReflectionLog


class SelfReflectionCommandTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Self", specialty="t")

    @patch(
        "assistants.management.commands.reflect_on_self.AssistantReflectionEngine.generate_reflection"
    )
    def test_self_reflection_updates_identity(self, mock_gen):
        mock_gen.return_value = (
            "I improved.{\n\"persona_summary\":\"new\",\"traits\":{\"curious\":true},\"values\":[\"clarity\"],\"motto\":\"Try\"}"
        )
        call_command("reflect_on_self", assistant=self.assistant.slug)
        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.persona_summary, "new")
        self.assertTrue(self.assistant.traits["curious"])
        self.assertEqual(self.assistant.values, ["clarity"])
        self.assertEqual(self.assistant.motto, "Try")
        log = AssistantReflectionLog.objects.filter(
            assistant=self.assistant, category="self_reflection"
        ).first()
        self.assertIsNotNone(log)


class IdentityPromptTest(APITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(
            name="Id",
            specialty="t",
            persona_summary="cheerful helper",
            motto="Be kind",
        )
        self.url = f"/api/assistants/{self.assistant.slug}/chat/"

    def _make_completion(self):
        class Msg:
            content = "ok"

        class Choice:
            message = Msg()

        class Usage:
            prompt_tokens = 1
            completion_tokens = 1
            total_tokens = 2

        class Completion:
            def __init__(self):
                self.choices = [Choice()]
                self.usage = Usage()

        return Completion()

    @patch("assistants.views.assistants.client.chat.completions.create")
    def test_identity_in_system_prompt(self, mock_create):
        captured = {}

        def side_effect(**kwargs):
            captured["messages"] = kwargs.get("messages")
            return self._make_completion()

        mock_create.side_effect = side_effect
        self.client.post(
            self.url,
            {"message": "hi", "session_id": str(uuid.uuid4())},
            format="json",
        )
        system_prompt = captured["messages"][0]["content"]
        self.assertIn("cheerful helper", system_prompt)
        self.assertIn("Be kind", system_prompt)

    @patch("assistants.views.assistants.client.chat.completions.create")
    def test_identity_persists_across_sessions(self, mock_create):
        prompts = []

        def side_effect(**kwargs):
            prompts.append(kwargs.get("messages")[0]["content"])
            return self._make_completion()

        mock_create.side_effect = side_effect
        self.client.post(
            self.url,
            {"message": "one", "session_id": str(uuid.uuid4())},
            format="json",
        )
        self.client.post(
            self.url,
            {"message": "two", "session_id": str(uuid.uuid4())},
            format="json",
        )
        self.assertEqual(prompts[0], prompts[1])
