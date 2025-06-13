import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor


class SuggestMissingMutationsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", slug="claritybot")
        SymbolicMemoryAnchor.objects.create(
            slug="term",
            label="Term",
            assistant=self.assistant,
            fallback_score=1.0,
            memory_context=self.assistant.memory_context,
        )

    @patch(
        "memory.management.commands.generate_missing_mutations.call_gpt4",
        return_value="Better",
    )
    def test_api_suggest_missing(self, mock_call):
        resp = self.client.post(
            "/api/glossary/mutations/suggest-missing/",
            {"assistant": "claritybot"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["updated"], 1)
        self.assertEqual(data["stats"]["total"], 1)

    @patch(
        "memory.management.commands.generate_missing_mutations.call_gpt4",
        side_effect=Exception("boom"),
    )
    def test_api_error_handling(self, mock_call):
        resp = self.client.post(
            "/api/glossary/mutations/suggest-missing/",
            {"assistant": "claritybot"},
            format="json",
        )
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error", resp.json())

    @patch(
        "memory.management.commands.generate_missing_mutations.call_gpt4",
        return_value="Better",
    )
    def test_command_output(self, mock_call):
        out = StringIO()
        call_command(
            "generate_missing_mutations",
            "--assistant",
            "claritybot",
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn("Updated", output)

