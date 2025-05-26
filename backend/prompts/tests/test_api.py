import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from rest_framework.test import APITestCase
from prompts.models import Prompt
from unittest.mock import patch


class PromptAPITest(APITestCase):
    def setUp(self):
        self.prompt1 = Prompt.objects.create(
            title="Prompt One", content="Test", source="unit", type="system"
        )
        self.prompt2 = Prompt.objects.create(
            title="Prompt Two", content="Another", source="unit", type="user"
        )

    def test_list_prompts_show_all(self):
        resp = self.client.get("/api/prompts/?show_all=true")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        slugs = [p["slug"] for p in data]
        self.assertIn(self.prompt1.slug, slugs)
        self.assertIn(self.prompt2.slug, slugs)

    def test_create_and_fetch_prompt(self):
        payload = {
            "title": "Created", "content": "Hello", "source": "api", "type": "system"
        }
        resp = self.client.post("/api/prompts/create/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        slug = resp.json().get("slug")
        self.assertIsNotNone(slug)

        detail = self.client.get(f"/api/prompts/{slug}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json().get("slug"), slug)

    @patch("prompts.utils.mutation.call_llm", return_value="mutated text")
    def test_mutate_prompt(self, mock_call):
        payload = {"text": "sample", "mutation_type": "clarify", "tone": "neutral"}
        resp = self.client.post("/api/prompts/mutate/", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("result"), "mutated text")
        mock_call.assert_called()

    def test_mutate_prompt_missing_text_or_mode(self):
        resp = self.client.post(
            "/api/prompts/mutate/",
            {"text": "", "mutation_type": "clarify"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
